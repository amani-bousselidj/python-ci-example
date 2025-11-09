from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys
class بوت_الأخبار:
    def __init__(self):
        self.إعداد_المتصفح()
    
    # ...existing code...
    def إعداد_المتصفح(self):
        """إعداد متصفح Chrome تلقائياً"""
        الخيارات = webdriver.ChromeOptions()
        # جعل الوضع الخفي قابل للتعطيل عبر متغير بيئة HEADLESS (0 = عرض المتصفح)
        if os.getenv("HEADLESS", "1") == "1":
            الخيارات.add_argument('--headless')
        الخيارات.add_argument('--no-sandbox')
        
        # استخدام برنامج تشغيل محلي إذا عُيّن مسار عبر متغير بيئة CHROME_DRIVER_PATH
        محلي = os.getenv("CHROME_DRIVER_PATH")
        # إذا عَُيّن NO_DOWNLOAD=1 سنمنع التنزيل التلقائي (مفيدة عند اتصال بطيء)
        NO_DOWNLOAD = os.getenv("NO_DOWNLOAD", "0") == "1"
        try:
            if محلي and os.path.exists(محلي):
                print(f"استخدام ChromeDriver محلي: {محلي}")
                self.متصفح = webdriver.Chrome(
                    service=Service(محلي),
                    options=الخيارات
                )
            else:
                if NO_DOWNLOAD:
                    raise RuntimeError(
                        "لم يتم العثور على ChromeDriver محلي و NO_DOWNLOAD=1. "
                        "اضبط متغير البيئة CHROME_DRIVER_PATH إلى مسار chromedriver.exe أو أوقف NO_DOWNLOAD."
                    )
                print("لا يوجد ChromeDriver محلي، سيتم تنزيله تلقائياً (قد يستغرق وقتاً)...")
                # fallback: تنزيل تلقائي (قد يستغرق وقتاً حسب الشبكة)
                self.متصفح = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=الخيارات
                )
        except Exception as e:
            print("خطأ أثناء إعداد ChromeDriver:", e)
            raise
# ...existing code...
    
    def جمع_العناوين(self, الرابط):
        """يجلب عناوين الأخبار من موقع"""
        self.متصفح.get(الرابط)
        time.sleep(3)  # انتظار تحميل الصفحة
        
        # البحث عن عناصر الأخبار (تختلف حسب الموقع)
        عناوين = self.متصفح.find_elements(By.TAG_NAME, 'h3')
        
        الأخبار = []
        for عنوان in عناوين[:5]:  # أول 5 أخبار
            if عنوان.text.strip():
                الأخبار.append(عنوان.text)
        
        return الأخبار
    
    def حفظ_الأخبار(self, الأخبار, اسم_الملف='الأخبار.txt'):
        """حفظ الأخبار في ملف"""
        with open(اسم_الملف, 'w', encoding='utf-8') as ملف:
            ملف.write("آخر الأخبار:\n")
            ملف.write("=" * 30 + "\n")
            for i, خبر in enumerate(الأخبار, 1):
                ملف.write(f"{i}. {خبر}\n")
        
        print(f"✓ تم حفظ {len(الأخبار)} خبر في {اسم_الملف}")
    
    def إغلاق(self):
        """إغلاق المتصفح"""
        self.متصفح.quit()

# استخدام البوت
def main():
    # يمكن التحكم بالسلوك عبر متغيرات البيئة:
    # HEADLESS=0  -> لعرض نافذة المتصفح أثناء التجريب
    # CHROME_DRIVER_PATH=C:\path\to\chromedriver.exe  -> لتجنب التنزيل
    # NO_DOWNLOAD=1 -> إذا لم ترغب بتنزيل chromedriver تلقائياً
    بوت = بوت_الأخبار()
    try:
        أخبار = بوت.جمع_العناوين('https://www.bbc.com/arabic')
        # طباعة سريعة للعناوين في الكونسول
        for i, خبر in enumerate(أخبار, 1):
            print(f"{i}. {خبر}")
        بوت.حفظ_الأخبار(أخبار)
    except Exception as e:
        print("حدث خطأ أثناء التشغيل:", e)
        # كود خروج غير صفر عند فشل الإعداد
        sys.exit(1)
    finally:
        try:
            بوت.إغلاق()
        except Exception:
            pass


if __name__ == '__main__':
    main()