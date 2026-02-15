import telebot
import random
from telebot import types

# التوكن الخاص بك الذي أرسلته
TOKEN = '8074252682:AAEVcKbV4oAz4nY44Pin6TnpsRuV8N74nds'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🛡️ **أهلاً بك في بوت التوعية الأمنية**\n\n"
        "هذا البوت مصمم لأغراض تعليمية فقط تحت إشراف محمود أبو الفضل.\n"
        "استخدم الأوامر التالية:\n"
        "/gen + BIN - لتوليد أرقام تجريبية (مثال: `/gen 484733`)\n"
        "/info - لمعرفة مخاطر الفيزا الوهمية"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info_message(message):
    info_text = (
        "⚠️ **رسالة توعوية:**\n"
        "الأرقام التي يولدها هذا البوت هي أرقام عشوائية تماماً.\n"
        "1. لا تحتوي على رصيد حقيقي.\n"
        "2. استخدامها في محاولة الاحتيال يعرضك للمسائلة القانونية.\n"
        "3. احذر من المواقع التي تطلب بيانات بطاقتك الحقيقية مقابل وعود وهمية."
    )
    bot.send_message(message.chat.id, info_text, parse_mode="Markdown")

@bot.message_handler(commands=['gen'])
def generate_cards(message):
    try:
        # استخراج الـ BIN من الرسالة
        msg_parts = message.text.split()
        if len(msg_parts) < 2:
            bot.reply_to(message, "❌ يرجى إدخال الـ BIN بعد الأمر. مثال: `/gen 484733`", parse_mode="Markdown")
            return

        bin_val = msg_parts[1]
        
        if len(bin_val) != 6:
            bot.reply_to(message, "⚠️ الـ BIN يجب أن يتكون من 6 أرقام فقط.")
            return

        results = []
        for _ in range(5):  # توليد 5 بطاقات فقط
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            month = random.randint(1, 12)
            year = random.randint(2025, 2030)
            cvv = random.randint(100, 999)
            
            card = f"`{bin_val}{random_digits}|{month:02d}|{year}|{cvv}`"
            results.append(card)

        response = "✅ **الأرقام المولدة (للتجربة العلمية):**\n\n" + "\n".join(results)
        bot.reply_to(message, response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء التوليد، تأكد من إدخال أرقام فقط.")

print("البوت يعمل الآن...")
bot.polling()