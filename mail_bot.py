import telebot
import smtplib
import math
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------
# إعدادات البريد الإلكتروني (تم التحديث)
# ---------------------------------------------------------

fromaddr = "iphone011012013@gmail.com"
# ملاحظة: يفضل إزالة المسافات من كلمة المرور لضمان عملها بشكل صحيح مع بعض المكتبات
password = "qrpf wkub heck bnbi" 

# ---------------------------------------------------------
# دوال التشفير والإرسال
# ---------------------------------------------------------

def generateOTP():
    """توليد رمز مكون من 6 أرقام"""
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def sendcode(mail, code):
    """ارسال الرمز عبر Gmail SMTP"""
    toaddr = mail

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "رمز التحقق الخاص بك (Face ID Bot)"

    body = f"رمز التحقق هو: {code}\nلا تشارك هذا الرمز مع أحد."
    txt = MIMEText(body, 'plain', 'utf-8')
    msg.attach(txt)

    try:
        # الاتصال بسيرفر Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # نقوم بإزالة المسافات من كلمة المرور لضمان القبول
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.reply_to(message, "أهلاً بك! 👋\nأرسل بريدك الإلكتروني لاستلام رمز التحقق:")
    bot.register_next_step_handler(msg, process_email_step)

def process_email_step(message):
    email = message.text
    chat_id = message.chat.id

    # تحقق بسيط من صحة البريد
    if "@" not in email or "." not in email:
        msg = bot.reply_to(message, "بريد خاطئ! حاول مرة أخرى:")
        bot.register_next_step_handler(msg, process_email_step)
        return

    bot.send_message(chat_id, "⏳ جاري الإرسال...")

    otp_code = generateOTP()
    
    success = sendcode(email, otp_code)

    if success:
        bot.send_message(chat_id, f"✅ تم الإرسال بنجاح إلى {email}!")
        # (اختياري) يمكنك إظهار الرمز هنا للتجربة فقط، لكن يفضل إخفاؤه في التطبيق الحقيقي
        # bot.send_message(chat_id, f"الرمز المرسل (للتجربة): {otp_code}")
    else:
        bot.send_message(chat_id, "❌ فشل الإرسال. تأكد من صحة البريد المستقبل.")

print("Bot is running... (Press Ctrl+C to stop)")
bot.infinity_polling()