import telebot
import requests
import platform
import time

# التوكن الخاص بك
TOKEN = '8074252682:AAEVcKbV4oAz4nY44Pin6TnpsRuV8N74nds'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    # استخدام HTML بدلاً من Markdown لتجنب أخطاء الرموز الخاصة
    msg = (
        "🚀 <b>أهلاً بك في نظام AboElfadl الأمني المتكامل</b>\n\n"
        "هذا البوت يجمع أدوات الفحص والتوعية في مكان واحد:\n\n"
        "1️⃣ /check_site + الرابط : لفحص استجابة موقع\n"
        "2️⃣ /my_info : لعرض معلومات جهازك الحالية\n"
        "3️⃣ /security_tips : نصائح للتوعية ضد الاختراق\n\n"
        "👤 <i>إعداد: محمود أبو الفضل</i>"
    )
    bot.reply_to(message, msg, parse_mode="HTML")

@bot.message_handler(commands=['check_site'])
def check_site(message):
    try:
        # التأكد من وجود رابط بعد الأمر
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ يرجى إدخال الرابط بعد الأمر.\nمثال: `/check_site https://google.com`", parse_mode="Markdown")
            return

        url = args[1]
        if not url.startswith('http'):
            url = 'https://' + url

        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()
        
        res_msg = (
            f"🌐 <b>تقرير فحص الموقع:</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔗 <b>الرابط:</b> {url}\n"
            f"✅ <b>الحالة:</b> {response.status_code}\n"
            f"⚡ <b>سرعة الاستجابة:</b> {round(end_time - start_time, 2)} ثانية\n"
            f"━━━━━━━━━━━━━━"
        )
        bot.reply_to(message, res_msg, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء الفحص: {str(e)}")

@bot.message_handler(commands=['my_info'])
def my_info(message):
    info = (
        f"💻 <b>معلومات النظام:</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🖥️ <b>النظام:</b> {platform.system()}\n"
        f"⚙️ <b>الإصدار:</b> {platform.release()}\n"
        f"🏛️ <b>المعالج:</b> {platform.processor()}\n"
        f"━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, info, parse_mode="HTML")

@bot.message_handler(commands=['security_tips'])
def tips(message):
    tip_text = (
        "🛡️ <b>نصائح محمود أبو الفضل للتوعية:</b>\n\n"
        "• لا تفتح روابط مجهولة المصدر أبداً.\n"
        "• الأكواد المشفرة قد تحتوي على فيروسات خفية.\n"
        "• تفعيل التحقق بخطوتين هو خط دفاعك الأول."
    )
    bot.reply_to(message, tip_text, parse_mode="HTML")

print("البوت الاحترافي يعمل الآن بدون أخطاء...")
bot.polling()