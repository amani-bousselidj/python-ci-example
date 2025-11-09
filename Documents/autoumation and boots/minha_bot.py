#!/usr/bin/env python3
"""
minha_bot.py

بوت بسيط يفحص صفحة المواعيد https://minha.anem.dz/pre_rendez_vous
- يدعم استخدام chromedriver محلي عبر CHROME_DRIVER_PATH
- يمنع التنزيل التلقائي عند NO_DOWNLOAD=1
- يمكن تشغيله في وضع مستمر (افتراضي) أو مجدول عبر TIMES env var
- يعرض إشعار صوتي و (إن أمكن) إشعار سطح المكتب عند العثور على عنصر يدل على فتح المواعيد

تشغيل (PowerShell):
    set CHROME_DRIVER_PATH=C:\path\to\chromedriver.exe    # اختياري
    set NO_DOWNLOAD=1                                       # لمنع التنزيل التلقائي إذا لديك chromedriver محلي
    set HEADLESS=0                                           # 0 لعرض نافذة المتصفح أثناء التجريب
    python .\minha_bot.py                                   # فحص مستمر

أو لتشغيل مجدول في أوقات محددة (مثال):
    set TIMES=08:00,12:00,16:00
    python .\minha_bot.py

عدل دالة `check_appointment_open` لملائمة الـ DOM إذا عرفت محددات دقيقة من أدوات المطور.
"""

import os
import sys
import time
import datetime
from typing import List, Tuple

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
except Exception as e:
    print("مطلوب تثبيت selenium. ثبتها باستخدام: pip install selenium webdriver-manager")
    raise

def parse_times(env_var: str = "TIMES") -> List[Tuple[int, int]]:
    s = os.getenv(env_var, "").strip()
    if not s:
        return []
    parts = [p.strip() for p in s.split(",") if p.strip()]
    out = []
    for p in parts:
        try:
            hh, mm = p.split(":")
            out.append((int(hh), int(mm)))
        except Exception:
            print(f"تجاهل وقت غير صالح: {p}")
    return out

class MinhaBot:
    def __init__(self, headless: bool = True, implicit_wait: int = 6):
        self.headless = headless
        self.driver = None
        self.implicit_wait = implicit_wait
        self.setup_driver()

    def setup_driver(self):
        opts = webdriver.ChromeOptions()
        # Headless قد يختلف بين إصدارات الكروم -> نستخدم الخيار المحدث إن وُجد
        if self.headless:
            try:
                opts.add_argument("--headless=new")
            except Exception:
                opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        path = os.getenv("CHROME_DRIVER_PATH")
        no_download = os.getenv("NO_DOWNLOAD", "0") == "1"
        try:
            if path and os.path.exists(path):
                print(f"استخدام chromedriver محلي: {path}")
                self.driver = webdriver.Chrome(service=Service(path), options=opts)
            else:
                if no_download:
                    raise RuntimeError("لم يُعثر على chromedriver محلي و NO_DOWNLOAD=1.")
                # تنزيل تلقائي
                from webdriver_manager.chrome import ChromeDriverManager
                print("تنزيل chromedriver تلقائياً (مرة واحدة)...")
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            self.driver.implicitly_wait(self.implicit_wait)
        except Exception as e:
            print("خطأ أثناء إعداد المتصفح:", e)
            raise

    def open_page(self, url: str):
        self.driver.get(url)

    def check_appointment_open(self, allow: List[str] = None, exclude: List[str] = None):
        """
        تفحص DOM لمعرفة ما إذا كانت صفحة المواعيد مفتوحة.
        نستخدم قائمة منطقية متعددة لمحاولة اكتشاف الزر/النص الصحيح.
        عدِّل هذا لو عرفت محددات أدق من أدوات المطور في الصفحة.
        """
        try:
            found_flag = False
            # حالة 1: زر أو رابط يحوي نصاً بالفرنسية متعلقًا بـ "rendez" أو "rendez-vous"
            xpaths = [
                "//button[contains(translate(., 'R', 'r'), 'rendez')]",
                "//a[contains(translate(., 'R', 'r'), 'rendez')]",
                "//button[contains(., 'Prendre') or contains(., 'prendre')]",
                "//button[contains(., 'حجز') or contains(., 'موعد')]",
                "//a[contains(., 'حجز') or contains(., 'موعد')]",
            ]
            for xp in xpaths:
                elems = self.driver.find_elements(By.XPATH, xp)
                if elems:
                    # رجع True فقط إذا العنصر ظاهر وليس مخفيًا
                    for el in elems:
                        try:
                            if el.is_displayed():
                                found_flag = True
                                break
                        except Exception:
                            found_flag = True
                            break
                    if found_flag:
                        break

            # حالة 2: عنصر بصنف واضح (مثال: btn, alert أو container يظهر عند فتح التسجيل)
            selectors = [
                "button[class*='btn']",
                "a[class*='btn']",
                "div.alert",
            ]
            for sel in selectors:
                elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    # تحقق من وجود نص يشير إلى فتح الموعد
                    for el in elems:
                        txt = el.text or ""
                        if any(k in txt.lower() for k in ["rendez", "prendre", "حجز", "موعد"]):
                            found_flag = True
                            break
                    if found_flag:
                        break

            # حالة 3: تحقق من وجود عناصر فورم أو حقول تتاح عند الفتح (مؤشر عام)
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            if forms and len(forms) > 0:
                # إن وُجد نموذج مخصص للتسجيل، نعتبر ذلك إشارة
                found_flag = True

            # الآن جمع مقتطف نصي لتحديد الوكالات المتطابقة
            snippet = self.extract_snippet(400)
            matches = []
            if allow:
                for a in allow:
                    if a.lower() in snippet.lower():
                        matches.append(a)
            if exclude:
                for a in exclude:
                    if a.lower() in snippet.lower():
                        # إذا وُجد اسم مستبعد في المقتطف نعتبر النتيجة غير مطابقة
                        return False, [], snippet

            # لو وجد مؤشر عام وفلتر السماح موجود لكن لم يطابق شيء -> اعتبره غير مطابق
            if found_flag:
                if allow and len(matches) == 0:
                    return False, [], snippet
                return True, matches, snippet

            return False, [], snippet
        except Exception as e:
            print("خطأ أثناء فحص الصفحة:", e)
            return False, [], ""

    def notify(self):
        print("*** المواعيد متاحة الآن! ***)")
        # صوت بسيط على ويندوز
        try:
            import winsound
            winsound.Beep(800, 800)
        except Exception:
            pass
        # إشعار سطح المكتب إن كان متاحًا
        try:
            from win10toast import ToastNotifier
            t = ToastNotifier()
            t.show_toast("Minha Bot", "المواعيد متاحة الآن!", duration=10)
        except Exception:
            pass

    def close(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass

    def extract_snippet(self, maxlen: int = 200) -> str:
        """محاولة الحصول على مقتطف نصي مفيد من الصفحة لتضمينه في السجل."""
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            txt = body.text or ""
            s = ' '.join(txt.split())
            return s[:maxlen]
        except Exception:
            return ""


def run_continuous(bot: MinhaBot, url: str, interval_seconds: int = 60):
    results_file = os.getenv('RESULTS_FILE', 'minha_results.txt')
    # قراءة فلتر الوكالات من المتغيرات البيئية
    allow = os.getenv('AGENCIES_ALLOW', '').strip()
    exclude = os.getenv('AGENCIES_EXCLUDE', '').strip()
    allow_list = [a.strip() for a in allow.split(',') if a.strip()]
    exclude_list = [a.strip() for a in exclude.split(',') if a.strip()]
    print(f"فحص مستمر كل {interval_seconds} ثانية — فتح: {url} — السجل: {results_file}")
    if allow_list:
        print("فلتر السماح للوكالات:", allow_list)
    if exclude_list:
        print("فلتر استبعاد الوكالات:", exclude_list)
    try:
        while True:
            try:
                bot.open_page(url)
                # انتظر تحميل سريع
                time.sleep(3)
                found, matches, snippet = bot.check_appointment_open(allow_list or None, exclude_list or None)
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if found:
                    bot.notify()
                    matched_text = ','.join(matches) if matches else ''
                    line = f"{timestamp} | FOUND | {url} | matched: {matched_text} | snippet: {snippet}\n"
                    print("تم العثور على مؤشِّر فتح المواعيد المتطابقة مع الفلتر — سأنهي الفحص (يمكنك تعديل السلوك).")
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(line)
                    return
                else:
                    line = f"{timestamp} | NOT_FOUND | {url}\n"
                    print(f"{timestamp} — لا توجد مواعيد مناسبة بعد.")
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(line)
            except Exception as e:
                print("خطأ مؤقت أثناء الفحص:", e)
            time.sleep(interval_seconds)
    finally:
        bot.close()


def run_scheduled(bot: MinhaBot, url: str, times: List[Tuple[int, int]]):
    results_file = os.getenv('RESULTS_FILE', 'minha_results.txt')
    allow = os.getenv('AGENCIES_ALLOW', '').strip()
    exclude = os.getenv('AGENCIES_EXCLUDE', '').strip()
    allow_list = [a.strip() for a in allow.split(',') if a.strip()]
    exclude_list = [a.strip() for a in exclude.split(',') if a.strip()]
    print("وضع مجدول. الأوقات:", times, "السجل:", results_file)
    if allow_list:
        print("فلتر السماح للوكالات:", allow_list)
    if exclude_list:
        print("فلتر استبعاد الوكالات:", exclude_list)
    done_today = set()
    try:
        while True:
            now = datetime.datetime.now()
            if now.hour == 0 and now.minute == 0:
                done_today.clear()
            for t in times:
                if (now.hour, now.minute) == t and t not in done_today:
                    print(f"[{now.strftime('%Y-%m-%d %H:%M')}] فتح الصفحة وفحص المواعيد...")
                    try:
                        bot.open_page(url)
                        time.sleep(3)
                        found, matches, snippet = bot.check_appointment_open(allow_list or None, exclude_list or None)
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if found:
                            bot.notify()
                            matched_text = ','.join(matches) if matches else ''
                            line = f"{timestamp} | FOUND | {url} | matched: {matched_text} | snippet: {snippet}\n"
                            with open(results_file, 'a', encoding='utf-8') as f:
                                f.write(line)
                        else:
                            print("لم تُفتح المواعيد المناسبة بعد.")
                            line = f"{timestamp} | NOT_FOUND | {url}\n"
                            with open(results_file, 'a', encoding='utf-8') as f:
                                f.write(line)
                    except Exception as e:
                        print("خطأ أثناء الفحص المجدول:", e)
                    done_today.add(t)
            time.sleep(15)
    finally:
        bot.close()


def main():
    url = os.getenv("MINHA_URL", "https://minha.anem.dz/pre_rendez_vous")
    headless = os.getenv("HEADLESS", "1") == "1"
    interval = int(os.getenv("INTERVAL", "60"))
    times = parse_times("TIMES")

    bot = MinhaBot(headless=headless)
    try:
        if times:
            run_scheduled(bot, url, times)
        else:
            run_continuous(bot, url, interval_seconds=interval)
    finally:
        bot.close()


if __name__ == '__main__':
    main()
