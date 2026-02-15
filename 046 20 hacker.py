import pyautogui
import win32gui
import time
import os
import datetime
import pyperclip  # مكتبة التعامل مع الحافظة

# --- إعدادات التحكم ---
SCREENSHOT_INTERVAL = 10  # تصوير الشاشة كل 10 ثواني
CHECK_INTERVAL = 1        # فحص الحافظة والنوافذ كل ثانية

# إعداد المجلدات
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
BASE_FOLDER = f"Safe_Monitor_{TODAY}"

if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER)

LOG_PATH = os.path.join(BASE_FOLDER, "Full_Report.txt")

def get_active_window():
    """جلب اسم النافذة الحالية"""
    try:
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except:
        return "Unknown"

def monitor_system():
    print(f"[*] تم تشغيل نظام المراقبة الآمن (Offline).")
    print(f"[*] يتم حفظ البيانات في: {BASE_FOLDER}")
    
    last_window = ""
    last_clipboard = ""
    last_screenshot_time = time.time()

    try:
        while True:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # 1. فحص النافذة النشطة
            current_window = get_active_window()
            if current_window != last_window and current_window.strip() != "":
                with open(LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] [تبديل نافذة] -> {current_window}\n")
                print(f"-> نافذة جديدة: {current_window}")
                last_window = current_window

            # 2. فحص الحافظة (ما تم نسخه)
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != last_clipboard and current_clipboard.strip() != "":
                    with open(LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(f"[{timestamp}] [تم نسخ نص] -> {current_clipboard}\n")
                        f.write("-" * 30 + "\n")
                    print(f"-> تم نسخ نص جديد.")
                    last_clipboard = current_clipboard
            except:
                pass # تجاهل الأخطاء إذا كانت الحافظة فارغة أو تحتوي صورة

            # 3. التقاط الشاشة (بناءً على التوقيت المحدد)
            if time.time() - last_screenshot_time > SCREENSHOT_INTERVAL:
                img_name = f"Screen_{datetime.datetime.now().strftime('%H-%M-%S')}.png"
                img_path = os.path.join(BASE_FOLDER, img_name)
                
                try:
                    pyautogui.screenshot(img_path)
                    # تسجيل أن تم أخذ صورة في التقرير النصي لسهولة الرجوع
                    with open(LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(f"[{timestamp}] [صورة] تم حفظ لقطة الشاشة: {img_name}\n")
                except Exception as e:
                    print(f"خطأ في التصوير: {e}")
                
                last_screenshot_time = time.time()

            # راحة للمعالج
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n[!] تم إيقاف النظام.")

if __name__ == "__main__":
    monitor_system()