import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

try:
    # نضيف هوية المتصفح لتجنب رفض الطلب
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/118.0.0.0 Safari/537.36"
    }

    url = "https://en.wikipedia.org/wiki/Main_Page"
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        print(f"❌ Error: Failed to fetch page (status code {response.status_code})")
        exit()

    # تحليل الصفحة
    soup = BeautifulSoup(response.text, "html.parser")

    # استخراج أول 5 عناوين من الصفحة الرئيسية
    headlines = [a.get_text(strip=True) for a in soup.select("#mp-upper ul li a")[:5]]

    if not headlines:
        print("⚠️ No headlines found on Wikipedia main page.")
        exit()

    # حفظها في JSON مع التوقيت
    data = {
        "timestamp": datetime.now().isoformat(),
        "headlines": headlines
    }

    with open("wiki_headlines.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Saved {len(headlines)} headlines:")
    print(headlines)

except requests.exceptions.RequestException as e:
    print(f"🌐 Network error: {e}")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
