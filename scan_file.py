import os
import sys
import platform
import string
import requests
from datetime import datetime

# --- إعدادات التيليجرام ---
BOT_TOKEN = "8519648833:AAHeg8gNX7P1UZabWKcqeFJv0NAggRzS3Qs"
CHAT_ID = "1431886140"

# الألوان للعرض المحلي
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def send_telegram_msg(message):
    """دالة لإرسال الرسالة إلى البوت"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # لتنسيق الخط
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"{Colors.GREEN}[✓] تم إرسال التقرير للتيليجرام بنجاح.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[!] فشل الإرسال: {response.text}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] خطأ في الاتصال بالإنترنت: {e}{Colors.ENDC}")

def get_drives_or_storage():
    """اكتشاف مسارات التخزين"""
    paths_to_scan = []
    system_name = platform.system()

    if system_name == 'Windows':
        available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        for drive in available_drives:
            paths_to_scan.append(drive + "\\")
            
    elif system_name == 'Linux' or system_name == 'Android':
        if os.path.exists('/storage/emulated/0'): # Android Internal
            paths_to_scan.append('/storage/emulated/0')
            if os.path.exists('/storage'): # External / SD Card
                try:
                    for folder in os.listdir('/storage'):
                        if folder not in ['emulated', 'self']:
                            paths_to_scan.append(os.path.join('/storage', folder))
                except: pass
        else:
            paths_to_scan.append('/') 
            
    return paths_to_scan

def scan_single_path(path):
    """فحص مسار واحد وإرجاع النتيجة الخاصة به"""
    # تصفير العدادات لكل مسار جديد
    current_extensions = {
        '.php': 0, '.py': 0, '.png': 0, '.pdf': 0,
        '.mp4': 0, '.mp3': 0, '.jpeg': 0, '.jpg': 0,
        '.html': 0, '.txt': 0, '.bat': 0, '.zip': 0, '.rar': 0
    }
    total_files = 0
    
    print(f"{Colors.WARNING}[>>] جاري فحص: {path} ... يرجى الانتظار{Colors.ENDC}")
    
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    total_files += 1
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    
                    if ext in current_extensions:
                        current_extensions[ext] += 1
                except: continue
    except PermissionError:
        print(f"{Colors.FAIL}[!] لا توجد صلاحية للوصول الكامل لهذا المسار.{Colors.ENDC}")

    return current_extensions, total_files

def format_report(path, stats, total):
    """تجهيز شكل التقرير للإرسال"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # تنسيق الرسالة للتيليجرام
    msg = f"🚀 *تقرير فحص جديد* (AboElfadl Tool)\n"
    msg += f"📅 التاريخ: `{timestamp}`\n"
    msg += f"📂 المسار المفحوص: `{path}`\n"
    msg += "➖➖➖➖➖➖➖➖\n"
    
    # إضافة الإحصائيات التي ليست صفراً فقط لتقليل حجم الرسالة (اختياري، هنا سأعرض الكل كما طلبت)
    for ext, count in stats.items():
        if count > 0:
            msg += f"🔹 `{ext}` : {count}\n"
        else:
            msg += f"🔸 `{ext}` : 0\n" # يمكنك حذف هذا السطر إذا أردت إخفاء الأصفار
            
    msg += "➖➖➖➖➖➖➖➖\n"
    msg += f"📊 *إجمالي الملفات:* {total}"
    
    return msg

def main():
    clear_screen()
    print(f"{Colors.BOLD}{Colors.HEADER}--- أداة الفحص والإرسال للتيليجرام ---{Colors.ENDC}")
    
    # 1. تحديد المسارات
    paths = get_drives_or_storage()
    if not paths:
        print("لم يتم العثور على وحدات تخزين.")
        return

    print(f"المسارات المستهدفة: {paths}")
    send_telegram_msg(f"✅ *بدء عملية الفحص* \nالجهاز: {platform.node()} \nعدد الأقراص: {len(paths)}")

    # 2. الفحص والإرسال لكل مسار
    for path in paths:
        stats, total = scan_single_path(path)
        report_msg = format_report(path, stats, total)
        
        # عرض محلي
        print(f"{Colors.GREEN}[+] انتهى فحص {path}. الإجمالي: {total}{Colors.ENDC}")
        
        # إرسال للتيليجرام
        send_telegram_msg(report_msg)

    print(f"\n{Colors.BOLD}تم الانتهاء من جميع العمليات.{Colors.ENDC}")
    send_telegram_msg("🏁 *تم الانتهاء من الفحص الكلي للجهاز.*")

if __name__ == "__main__":
    main()