import telebot
from telebot import types
import requests
import platform
import base64
import phonenumbers
from phonenumbers import geocoder, carrier

# التوكن الخاص بك
TOKEN = '8074252682:AAEVcKbV4oAz4nY44Pin6TnpsRuV8N74nds'
bot = telebot.TeleBot(TOKEN)

# دالة لإنشاء الأزرار الرئيسية التي تظهر أسفل الشاشة
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📱 تحليل رقم هاتف")
    btn2 = types.KeyboardButton("🌐 فحص موقع")
    btn3 = types.KeyboardButton("🔐 تشفير Base64")
    btn4 = types.KeyboardButton("🔓 فك تشفير Base64")
    btn5 = types.KeyboardButton("🖥️ معلومات النظام")
    btn6 = types.KeyboardButton("🛡️ نصائح أمنية")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🛡️ <b>نظام AboElfadl الأمني المتكامل</b>\n\n"
        "مرحباً بك يا محمود في النسخة الاحترافية.\n"
        "استخدم الأزرار أدناه للوصول السريع للأدوات."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text == "📱 تحليل رقم هاتف":
        bot.send_message(chat_id, "👤 أرسل رقم الهاتف الآن مع مفتاح الدولة (مثال: +2010...)")

    elif text == "🌐 فحص موقع":
        bot.send_message(chat_id, "🔗 أرسل رابط الموقع لفحصه (مثال: google.com)")

    elif text == "🔐 تشفير Base64":
        bot.send_message(chat_id, "🔐 أرسل النص الذي تريد تشفيره")

    elif text == "🔓 فك تشفير Base64":
        bot.send_message(chat_id, "🔓 أرسل الكود المشفر لفك تشفيره")

    elif text == "🖥️ معلومات النظام":
        info = f"💻 <b>النظام:</b> {platform.system()}\n🏛️ <b>المعالج:</b> {platform.processor()}"
        bot.send_message(chat_id, info, parse_mode="HTML")

    elif text == "🛡️ نصائح أمنية":
        tips = (
            "🛡️ <b>نصائح محمود أبو الفضل للتوعية:</b>\n"
            "1. احذر الروابط المختصرة المجهولة.\n"
            "2. لا تشارك رموز التحقق (OTP) مع أحد.\n"
            "3. تأكد من فحص الملفات قبل فتحها."
        )
        bot.send_message(chat_id, tips, parse_mode="HTML")

    # معالجة المدخلات (تحليل الأرقام أو التشفير)
    elif text.startswith('+'):
        try:
            parsed = phonenumbers.parse(text, None)
            country = geocoder.description_for_number(parsed, "ar")
            op = carrier.name_for_number(parsed, "ar")
            res = f"📍 <b>نتائج تحليل الرقم:</b>\n🌍 الدولة: {country}\n🏢 الشركة: {op if op else 'غير معروفة'}"
            bot.reply_to(message, res, parse_mode="HTML")
        except:
            bot.reply_to(message, "❌ خطأ في تنسيق الرقم.")

    else:
        # محاولة فك تشفير تلقائي إذا أرسل نصاً عشوائياً يشبه Base64
        try:
            if len(text) > 8:
                dec = base64.b64decode(text).decode("utf-8")
                bot.reply_to(message, f"🔓 <b>فك تشفير تلقائي:</b>\n<code>{dec}</code>", parse_mode="HTML")
        except:
            bot.reply_to(message, "⚙️ اختر وظيفة من الأزرار بالأسفل أو أرسل بيانات صالحة.")

print("البوت الاحترافي بالأزرار الرئيسية يعمل الآن...")
bot.polling()