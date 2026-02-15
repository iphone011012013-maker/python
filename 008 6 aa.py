import telebot
from telebot import types
import random
import requests
import platform
import base64
import time
import re
import phonenumbers
from phonenumbers import geocoder, carrier, timezone, phonenumberutil

# ==========================================
# إعدادات البوت
# ==========================================
TOKEN = '8408417562:AAGbJ1VuFQ7nzTQhrTl72Atv5tkBmyFJWlU'
ADMIN_ID = 1431886140

bot = telebot.TeleBot(TOKEN)

# ==========================================
# لوحة التحكم الرئيسية (الأزرار)
# ==========================================
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("💳 توليد فيزا (BIN)")
    btn2 = types.KeyboardButton("📱 تحليل رقم هاتف")
    btn3 = types.KeyboardButton("✂️ اختصار روابط")
    btn4 = types.KeyboardButton("🌐 فحص حالة موقع")
    btn5 = types.KeyboardButton("🔐 تشفير/فك ملفات")
    btn6 = types.KeyboardButton("📝 تشفير/فك نصوص")
    btn7 = types.KeyboardButton("🖥️ معلومات النظام")
    btn8 = types.KeyboardButton("🛡️ نصائح أمنية")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    return markup

# ==========================================
# بداية البوت /start
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"🚀 **أهلاً بك في البوت الشامل المدمج**\n"
        f"المطور: [Admin](tg://user?id={ADMIN_ID})\n\n"
        "اختر الخدمة التي تريدها من القائمة بالأسفل 👇"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

# ==========================================
# معالج الأزرار والوظائف
# ==========================================
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id

    # 1. توليد فيزا
    if text == "💳 توليد فيزا (BIN)":
        msg = bot.reply_to(message, "🔢 أرسل الـ BIN الآن (أول 6 أرقام للبطاقة)\nمثال: `484733`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_visa_gen)

    # 2. تحليل رقم هاتف
    elif text == "📱 تحليل رقم هاتف":
        msg = bot.reply_to(message, "📞 أرسل الرقم مع مفتاح الدولة (مثال: +2010xxxx)")
        bot.register_next_step_handler(msg, process_phone_track)

    # 3. اختصار روابط
    elif text == "✂️ اختصار روابط":
        msg = bot.reply_to(message, "🔗 أرسل الرابط الطويل لاختصاره:")
        bot.register_next_step_handler(msg, process_url_shorten)

    # 4. فحص موقع
    elif text == "🌐 فحص حالة موقع":
        msg = bot.reply_to(message, "🌍 أرسل رابط الموقع (مثال: google.com):")
        bot.register_next_step_handler(msg, process_site_check)

    # 5. تشفير ملفات
    elif text == "🔐 تشفير/فك ملفات":
        markup = types.InlineKeyboardMarkup()
        btn_en = types.InlineKeyboardButton('تشفير ملف 🔒', callback_data='file_en')
        btn_de = types.InlineKeyboardButton('فك تشفير ملف 🔓', callback_data='file_de')
        markup.add(btn_en, btn_de)
        bot.reply_to(message, "اختر العملية المطلوبة للملفات:", reply_markup=markup)

    # 6. تشفير نصوص
    elif text == "📝 تشفير/فك نصوص":
        msg = bot.reply_to(message, "🔏 أرسل النص لتشفيره، أو كود Base64 لفك تشفيره:")
        bot.register_next_step_handler(msg, process_text_base64)

    # 7. معلومات النظام
    elif text == "🖥️ معلومات النظام":
        info = (
            f"💻 <b>معلومات الخادم:</b>\n"
            f"🖥️ <b>النظام:</b> {platform.system()}\n"
            f"⚙️ <b>الإصدار:</b> {platform.release()}\n"
            f"🏛️ <b>المعالج:</b> {platform.processor()}"
        )
        bot.reply_to(message, info, parse_mode="HTML")

    # 8. نصائح أمنية
    elif text == "🛡️ نصائح أمنية":
        tips = (
            "🛡️ <b>نصائح التوعية الأمنية:</b>\n\n"
            "1. الأرقام المولدة وهمية ولا تحتوي على رصيد.\n"
            "2. لا تفتح روابط مجهولة المصدر.\n"
            "3. تفعيل التحقق بخطوتين يحمي حسابك.\n"
            "4. لا تشارك أكواد التفعيل (OTP) مع أحد."
        )
        bot.reply_to(message, tips, parse_mode="HTML")
    
    else:
        # رد تلقائي إذا لم يفهم الأمر
        bot.reply_to(message, "⚠️ اختر أمراً من القائمة.", reply_markup=main_keyboard())

# ==========================================
# دوال المعالجة (Logic Functions)
# ==========================================

# --- معالج توليد الفيزا ---
def process_visa_gen(message):
    try:
        bin_val = message.text.strip()
        if not bin_val.isdigit() or len(bin_val) < 6:
            bot.reply_to(message, "⚠️ خطأ: يجب إرسال 6 أرقام على الأقل.", reply_markup=main_keyboard())
            return
            
        results = []
        for _ in range(10):  # توليد 10 بطاقات
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            month = random.randint(1, 12)
            year = random.randint(2025, 2030)
            cvv = random.randint(100, 999)
            card = f"`{bin_val[:6]}{random_digits}|{month:02d}|{year}|{cvv}`"
            results.append(card)

        response = "✅ **الأرقام المولدة (للتجربة العلمية):**\n\n" + "\n".join(results)
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=main_keyboard())
    except Exception:
        bot.reply_to(message, "حدث خطأ.", reply_markup=main_keyboard())

# --- معالج تحليل الرقم ---
def process_phone_track(message):
    try:
        num = message.text
        parsed_num = phonenumbers.parse(num, None)
        
        is_valid = phonenumbers.is_valid_number(parsed_num)
        number_type = phonenumberutil.number_type(parsed_num)
        
        type_str = "غير معروف"
        if number_type == phonenumberutil.PhoneNumberType.MOBILE: type_str = "جوال (Mobile)"
        elif number_type == phonenumberutil.PhoneNumberType.FIXED_LINE: type_str = "خط أرضي"

        country = geocoder.description_for_number(parsed_num, "ar")
        service_provider = carrier.name_for_number(parsed_num, "ar")
        time_zones = timezone.time_zones_for_number(parsed_num)
        intl_format = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        response = (
            f"🔎 **تقرير الرقم:** `{intl_format}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"✅ **الحالة:** {'صالح' if is_valid else 'غير صالح'}\n"
            f"🌍 **الدولة:** {country}\n"
            f"🏢 **الشركة:** {service_provider}\n"
            f"📱 **النوع:** {type_str}\n"
            f"⏰ **المنطقة:** {', '.join(time_zones)}"
        )
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=main_keyboard())
    except:
        bot.reply_to(message, "❌ تأكد من صيغة الرقم (مثال: +201xxxx)", reply_markup=main_keyboard())

# --- معالج اختصار الروابط ---
def process_url_shorten(message):
    msg = message.text
    if re.search("(?P<url>https?://[^\s]+)", msg):
        try:
            url = f'https://is.gd/create.php?format=simple&url={msg}'
            req = requests.get(url).text
            bot.reply_to(message, f'✅ **تم الاختصار:**\n{req}', parse_mode="Markdown", reply_markup=main_keyboard())
        except:
            bot.reply_to(message, "حدث خطأ في الاتصال بالخدمة.")
    else:
        bot.reply_to(message, "❌ هذا ليس رابطاً صالحاً.", reply_markup=main_keyboard())

# --- معالج فحص المواقع ---
def process_site_check(message):
    url = message.text
    if not url.startswith('http'):
        url = 'https://' + url
    
    bot.reply_to(message, "⏳ جارِ الفحص...", parse_mode="Markdown")
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        res_msg = (
            f"🌐 <b>تقرير الموقع:</b>\n"
            f"🔗 <b>الرابط:</b> {url}\n"
            f"✅ <b>كود الحالة:</b> {response.status_code}\n"
            f"⚡ <b>الوقت:</b> {round(end_time - start_time, 2)} ثانية"
        )
        bot.reply_to(message, res_msg, parse_mode="HTML", reply_markup=main_keyboard())
    except Exception as e:
        bot.reply_to(message, f"❌ الموقع لا يستجيب: {e}", reply_markup=main_keyboard())

# --- معالج تشفير النصوص ---
def process_text_base64(message):
    text = message.text
    try:
        # محاولة فك التشفير أولاً
        decoded = base64.b64decode(text).decode('utf-8')
        # التأكد إذا كان النص المفكوك مقروءاً، وإلا نفترض أن المستخدم يريد التشفير
        # (بشكل بسيط سنقوم بالتشفير إذا فشل فك التشفير، أو عرض الاثنين)
        bot.reply_to(message, f"🔓 **تم فك التشفير:**\n`{decoded}`", parse_mode="Markdown", reply_markup=main_keyboard())
    except:
        # إذا فشل فك التشفير، نقوم بالتشفير
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        bot.reply_to(message, f"🔐 **تم التشفير:**\n`{encoded}`", parse_mode="Markdown", reply_markup=main_keyboard())

# ==========================================
# معالجة الملفات (Callback Queries)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_file_callbacks(call):
    if call.data == 'file_en':
        msg = bot.send_message(call.message.chat.id, "📂 أرسل الملف الآن لتشفيره:")
        bot.register_next_step_handler(msg, file_encrypt_step)
    elif call.data == 'file_de':
        msg = bot.send_message(call.message.chat.id, "📂 أرسل الملف الآن لفك تشفيره:")
        bot.register_next_step_handler(msg, file_decrypt_step)

def file_encrypt_step(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            encoded_file = base64.b64encode(downloaded_file)
            
            # إرسال الملف كنص أو ملف جديد (يفضل ملف لتجنب حدود النص)
            bot.send_document(message.chat.id, encoded_file, caption="✅ تم التشفير")
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ: {e}")
    else:
        bot.reply_to(message, "❌ لم يتم إرسال ملف.", reply_markup=main_keyboard())

def file_decrypt_step(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            decoded_file = base64.b64decode(downloaded_file)
            
            bot.send_document(message.chat.id, decoded_file, caption="✅ تم فك التشفير")
        except Exception as e:
            bot.reply_to(message, "❌ الملف غير صالح أو غير مشفر بـ Base64.", reply_markup=main_keyboard())
    else:
        bot.reply_to(message, "❌ لم يتم إرسال ملف.", reply_markup=main_keyboard())

# ==========================================
# التشغيل
# ==========================================
print("Bot is running...")
bot.infinity_polling()