# Telegram Bot — إعداد وتشغيل (Windows / PowerShell)

هذا المجلد يحتوي على مشروع بوت تليجرام بسيط. الملفات الأساسية موجودة داخل `my-telegram-bot/bot.py`.

المطلوب قبل التشغيل:
- Python 3.10+ مثبت
- مفتاح بوت تليجرام في ملف `.env` (TELEGRAM_BOT_TOKEN)
- (اختياري) مفتاح API للطقس (WEATHER_API_KEY)

ملف المتطلبات موجود: `requirements.txt`.

خطوات سريعة (PowerShell):

1) إنشاء بيئة افتراضية وتثبيت الحزم (سطر واحد - لا حاجة لتفعيل يدوياً):

```powershell
# من داخل جذر المشروع
python -m venv .venv
# تثبيت الحزم عبر pip المضمن في البيئة
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

2) إنشاء ملف `.env` بجانب `bot.py` أو في جذر المشروع (حسب تفضيلك). مثال محتوى `.env`:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEATHER_API_KEY=your_openweather_api_key_here
```

3) تشغيل البوت باستخدام بايثون البيئة:

```powershell
& ".\.venv\Scripts\python.exe" "my-telegram-bot\bot.py"
```

ملاحظات وأفضل ممارسات:
- لا تشارك توكن البوت أو مفاتيح API علنًا.
- إذا واجهت خطأ ModuleNotFoundError، تأكد من أنك تستخدم نفس `.venv` عند التثبيت والتشغيل.
- لتحديد مفسّر Python في VS Code: اضغط Ctrl+Shift+P -> Python: Select Interpreter -> اختَر `.venv` داخل المشروع.

لمزيد من المساعدة، أرسل الخطأ (traceback) كما ظهر في المحرّر أو الطرفية.
