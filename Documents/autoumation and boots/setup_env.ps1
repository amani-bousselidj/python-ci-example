# PowerShell helper: إنشاء بيئة افتراضية وتثبيت المتطلبات
param(
    [string]$venvPath = ".venv"
)

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python غير موجود في PATH. ثبت Python 3.10+ أولاً ثم أعد المحاولة."
    exit 1
}

# إنشاء venv إن لم يكن موجوداً
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

$py = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Error "فشل العثور على python في $venvPath. تأكد من إنشاء البيئة الافتراضية بنجاح."
    exit 1
}

Write-Output "استخدام: $py"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt

Write-Output "تم التثبيت! لتشغيل البوت: & \"$py\" \"my-telegram-bot\bot.py\""
