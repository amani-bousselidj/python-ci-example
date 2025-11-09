import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import requests
import json

# تحميل المتغيرات من ملف البيئة
load_dotenv()

class بوت_تليجرام_المتقدم:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.application = Application.builder().token(self.token).build()
        self.إعداد_المعالجات()
    
    def إعداد_المعالجات(self):
        """إعداد معالجات الأوامر والرسائل"""
        # معالجات الأوامر
        self.application.add_handler(CommandHandler("start", self.بدء))
        self.application.add_handler(CommandHandler("help", self.مساعدة))
        self.application.add_handler(CommandHandler("weather", self.طقس))
        self.application.add_handler(CommandHandler("quote", self.اقتباس))
        
        # معالجة الرسائل النصية العادية
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.معالجة_الرسالة))
    
    async def بدء(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        رسالة_الترحيب = f"""
        🎉 أهلاً بك {user.first_name}!
        
        أنا بوتك المساعد، يمكنني:
        
        🌤️ /weather [مدينة] - طقس أي مدينة
        💬 /quote - اقتباس عشوائي
        ℹ️ /help - المساعدة
        
        أرسل لي أي رسالة وسأرد عليك!
        """
        await update.message.reply_text(رسالة_الترحيب)
    
    async def مساعدة(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        رسالة_المساعدة = """
        📋 قائمة الأوامر المتاحة:
        
        /start - بدء الاستخدام
        /help - عرض هذه المساعدة
        /weather [مدينة] - الحصول على الطقس
        /quote - اقتباس ملهم
        
        💡 يمكنك أيضاً محادثتي بشكل طبيعي!
        """
        await update.message.reply_text(رسالة_المساعدة)
    
    async def طقس(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /weather"""
        if not context.args:
            await update.message.reply_text("⚠️ يرجى كتابة اسم المدينة\nمثال: /weather Riyadh")
            return
        
        المدينة = ' '.join(context.args)
        بيانات_الطقس = self.الحصول_على_الطقس(المدينة)
        
        if بيانات_الطقس:
            رسالة_الطقس = f"""
            🌤️ طقس {بيانات_الطقس['المدينة']}
            
            🌡️ درجة الحرارة: {بيانات_الطقس['درجة_الحرارة']}°C
            🤔 الشعور الفعلي: {بيانات_الطقس['الشعور_فعلي']}°C
            ☁️  الحالة: {بيانات_الطقس['الوصف']}
            💧 الرطوبة: {بيانات_الطقس['الرطوبة']}
            💨 الرياح: {بيانات_الطقس['سرعة_الرياح']}
            """
            await update.message.reply_text(رسالة_الطقس)
        else:
            await update.message.reply_text(f"❌ لم أتمكن من جلب طقس {المدينة}")
    
    async def اقتباس(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /quote"""
        اقتباس = self.الحصول_على_اقتباس()
        await update.message.reply_text(f"💬 {اقتباس}")
    
    async def معالجة_الرسالة(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل العادية"""
        نص_الرسالة = update.message.text.lower()
        user = update.effective_user
        
        # ردود ذكية بسيطة
        if any(كلمة in نص_الرسالة for كلمة in ['مرحبا', 'اهلا', 'السلام']):
            await update.message.reply_text(f"مرحباً {user.first_name}! 😊")
        elif any(كلمة in نص_الرسالة for كلمة in ['شكرا', 'مشكور']):
            await update.message.reply_text("العفو! 💙")
        elif 'طقس' in نص_الرسالة:
            await update.message.reply_text("استخدم /weather متبوعاً باسم المدينة 🌤️")
        else:
            await update.message.reply_text("💡 جرب /help لرؤية جميع الأوامر المتاحة")
    
    def الحصول_على_الطقس(self, المدينة):
        """دالة مساعدة لجلب الطقس"""
        try:
            # استخدام API مجانية للطقس
            response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather",
                params={
                    'q': المدينة,
                    'appid': os.getenv('WEATHER_API_KEY'),
                    'units': 'metric',
                    'lang': 'ar'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'المدينة': data['name'],
                    'درجة_الحرارة': data['main']['temp'],
                    'الشعور_فعلي': data['main']['feels_like'],
                    'الوصف': data['weather'][0]['description'],
                    'الرطوبة': f"{data['main']['humidity']}%",
                    'سرعة_الرياح': f"{data['wind']['speed']} m/s"
                }
        except:
            pass
        return None
    
    def الحصول_على_اقتباس(self):
        """دالة مساعدة لجلب الاقتباس"""
        try:
            response = requests.get("https://api.quotable.io/random", timeout=5)
            data = response.json()
            return f"\"{data['content']}\" - {data['author']}"
        except:
            return "الحياة رحلة، استمتع بكل لحظة فيها. 🌟"
    
    def تشغيل(self):
        """تشغيل البوت"""
        print("🤖 بدأ تشغيل بوت تليجرام...")
        self.application.run_polling()

# ملف .env يجب أن يحتوي:
# TELEGRAM_BOT_TOKEN=your_bot_token_here
# WEATHER_API_KEY=your_weather_api_key_here