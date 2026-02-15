import telebot
import pyautogui
import pyperclip
import os
import time
import webbrowser
import win32gui
from threading import Thread

# --- إعدادات البوت ---
TOKEN = "7441270348:AAE7SFRVxepMoBIw2IGXsbtVM0cf5ryBXAA"
MY_ID = 1431886140  # الـ ID الخاص بك فقط لضمان الأمان

bot = telebot.TeleBot(TOKEN)

# --- دالة التحقق من الهوية (Security Check) ---
def is_authorized(message):
    """تتأكد أن الأمر قادم منك أنت فقط وليس شخص غريب"""
    if message.chat.id == MY_ID:
        return True
    else:
        bot.reply_to(message, "⛔ غير مصرح لك باستخدام هذا البوت.")
        print(f"[!] محاولة دخول غير مصرحة من ID: {message.chat.id}")
        return False

# --- أوامر التحكم (Command Handlers) ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message): return
    
    help_text = """
    👮‍♂️ **لوحة تحكم المدير:**
    
    /screen - 📸 أخذ لقطة شاشة فورية
    /clip   - 📋 عرض محتوى الحافظة (المنسوخ)
    /close  - ❌ إغلاق البرنامج النشط حالياً
    /open [رابط] - 🌐 فتح موقع (مثال: /open google.com)
    /info   - ℹ️ معرفة اسم النافذة المفتوحة الآن
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['screen'])
def send_screenshot(message):
    if not is_authorized(message): return
    
    bot.send_message(message.chat.id, "📸 جاري التقاط الشاشة...")
    
    # التقاط وحفظ الصورة
    img_name = "temp_screen.png"
    pyautogui.screenshot(img_name)
    
    # إرسال الصورة
    with open(img_name, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"⏰ {time.strftime('%H:%M:%S')}")
    
    # حذف الصورة المؤقتة لتوفير المساحة
    os.remove(img_name)

@bot.message_handler(commands=['clip'])
def get_clipboard(message):
    if not is_authorized(message): return
    
    try:
        content = pyperclip.paste()
        if content:
            bot.reply_to(message, f"📋 **محتوى الحافظة:**\n\n{content}")
        else:
            bot.reply_to(message, "الحافظة فارغة.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {str(e)}")

@bot.message_handler(commands=['close'])
def close_active_window(message):
    if not is_authorized(message): return
    
    # الحصول على اسم النافذة قبل غلقها
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        
        # محاكاة ضغط Alt + F4
        pyautogui.hotkey('alt', 'f4')
        
        bot.reply_to(message, f"✅ تم إرسال أمر الإغلاق للنافذة:\n{title}")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء الإغلاق: {e}")

@bot.message_handler(commands=['open'])
def open_url(message):
    if not is_authorized(message): return
    
    # استخراج الرابط من الرسالة (مثال: /open google.com)
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            url = parts[1]
            webbrowser.open(url)
            bot.reply_to(message, f"✅ تم فتح الرابط: {url}")
        else:
            bot.reply_to(message, "⚠️ يرجى كتابة الرابط بعد الأمر.\nمثال: /open google.com")
    except Exception as e:
        bot.reply_to(message, f"خطأ: {e}")

@bot.message_handler(commands=['info'])
def get_info(message):
    if not is_authorized(message): return
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        bot.reply_to(message, f"💻 **النافذة النشطة الآن:**\n{title}")
    except:
        bot.reply_to(message, "غير معروف.")

# --- تشغيل البوت ---
print("✅ تم تشغيل بوت التحكم عن بعد...")
print("انتظار الأوامر...")

# هذا الأمر يجعل البوت يعمل بشكل دائم لاستقبال الرسائل
bot.infinity_polling()