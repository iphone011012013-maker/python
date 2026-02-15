import telebot
import smtplib
import math
import random
import time  # مكتبة للانتظار بين الرسائل لتجنب الحظر
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------
# إعدادات البريد الإلكتروني
# ---------------------------------------------------------

fromaddr = "iphone011012013@gmail.com"
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

def sendcode(mail, code, index, total):
    """ارسال الرمز عبر Gmail SMTP"""
    toaddr = mail

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    # نغير العنوان ليكون مميزاً لكل رسالة
    msg['Subject'] = f"رمز التحقق رقم ({index} من {total})"

    body = f"رمز التحقق الخاص بك هو: {code}\nهذه الرسالة رقم {index} من أصل {total} رسائل مطلوبة."
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = bot.reply_to(message, "أهلاً بك! 🚀\nأرسل بريدك الإلكتروني المستلم:")
    bot.register_next_step_handler(msg, process_email_step)

def process_email_step(message):
    email = message.text
    
    # التحقق من صحة البريد
    if "@" not in email or "." not in email:
        msg = bot.reply_to(message, "بريد خاطئ! حاول مرة أخرى:")
        bot.register_next_step_handler(msg, process_email_step)
        return

    # الانتقال للخطوة التالية: طلب العدد
    msg = bot.reply_to(message, "كم عدد رموز OTP التي تريد إرسالها؟ (أدخل رقماً، مثلاً 5):")
    # نمرر الإيميل للدالة التالية لكي لا نفقده
    bot.register_next_step_handler(msg, process_count_step, email)

def process_count_step(message, email):
    try:
        count = int(message.text)
        
        # وضع حد أقصى للحماية من التشنج أو الحظر
        if count > 20:
            bot.reply_to(message, "⚠️ العدد كبير جداً! الحد الأقصى هو 20 رسالة في المرة الواحدة.")
            return
        if count <= 0:
            bot.reply_to(message, "الرجاء إدخال رقم صحيح أكبر من صفر.")
            return

    except ValueError:
        bot.reply_to(message, "الرجاء إدخال أرقام فقط (مثلاً: 5).")
        return

    chat_id = message.chat.id
    bot.send_message(chat_id, f"✅ سأبدأ الآن بإرسال {count} رموز إلى {email}...")

    success_count = 0
    
    # حلقة التكرار للإرسال
    for i in range(1, count + 1):
        otp_code = generateOTP()
        
        # محاولة الإرسال
        if sendcode(email, otp_code, i, count):
            bot.send_message(chat_id, f"📤 تم إرسال الرمز {i}/{count} بنجاح.")
            success_count += 1
        else:
            bot.send_message(chat_id, f"❌ فشل إرسال الرمز {i}/{count}.")
        
        # انتظار لمدة ثانيتين بين كل رسالة والأخرى لتجنب حظر جوجل (Anti-Spam)
        time.sleep(2)

    bot.send_message(chat_id, f"🏁 انتهت العملية.\nتم إرسال {success_count} رسالة بنجاح من أصل {count}.")

print("Bot is running... (Press Ctrl+C to stop)")
bot.infinity_polling()