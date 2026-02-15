import os
import sys
import platform
import string
from datetime import datetime

# الألوان
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# الامتدادات المستهدفة (تم تعريفها كمتغير عام لتجميع النتائج من كل الأقراص)
TARGET_EXTENSIONS = {
    '.php': 0, '.py': 0, '.png': 0, '.pdf': 0,
    '.mp4': 0, '.mp3': 0, '.jpeg': 0, '.jpg': 0,
    '.html': 0, '.txt': 0, '.bat': 0, '.zip': 0, '.rar': 0
}

TOTAL_SCANNED_FILES = 0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_drives_or_storage():
    """
    دالة ذكية لاكتشاف مسارات التخزين بناءً على الجهاز
    """
    paths_to_scan = []
    system_name = platform.system()

    if system_name == 'Windows':
        print(f"{Colors.BLUE}[*] تم اكتشاف نظام ويندوز. جاري البحث عن الأقراص...{Colors.ENDC}")
        # فحص جميع الحروف من A إلى Z لمعرفة الأقراص الموجودة
        available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        for drive in available_drives:
            paths_to_scan.append(drive + "\\")
            
    elif system_name == 'Linux' or system_name == 'Android':
        # التحقق هل نحن على أندرويد أم لينكس عادي
        if os.path.exists('/storage/emulated/0') or os.path.exists('/sdcard'):
            print(f"{Colors.BLUE}[*] تم اكتشاف نظام أندرويد.{Colors.ENDC}")
            # المسار الأساسي للذاكرة الداخلية
            paths_to_scan.append('/storage/emulated/0')
            
            # محاولة اكتشاف كارت الميموري (External SD)
            if os.path.exists('/storage'):
                try:
                    for folder in os.listdir('/storage'):
                        if folder not in ['emulated', 'self']:
                            paths_to_scan.append(os.path.join('/storage', folder))
                except PermissionError:
                    pass
        else:
            # لينكس عادي (لابتوب)
            print(f"{Colors.BLUE}[*] تم اكتشاف نظام لينكس.{Colors.ENDC}")
            paths_to_scan.append('/') # الحذر: فحص الروت قد يأخذ وقتاً طويلاً
            
    return paths_to_scan

def scan_path(path):
    global TOTAL_SCANNED_FILES
    print(f"{Colors.WARNING}[>>] جاري فحص: {path}{Colors.ENDC}")
    
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    TOTAL_SCANNED_FILES += 1
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    
                    if ext in TARGET_EXTENSIONS:
                        TARGET_EXTENSIONS[ext] += 1
                        
                    # طباعة تحديث كل 1000 ملف ليعرف المستخدم أن البرنامج يعمل
                    if TOTAL_SCANNED_FILES % 1000 == 0:
                        sys.stdout.write(f"\r{Colors.BLUE}تم فحص {TOTAL_SCANNED_FILES} ملف...{Colors.ENDC}")
                        sys.stdout.flush()

                except Exception:
                    continue # تخطي الملفات التالفة أو المحمية

    except PermissionError:
        print(f"{Colors.FAIL}[!] لا توجد صلاحية للوصول إلى: {path} (تم تخطيه){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] خطأ غير متوقع في {path}: {e}{Colors.ENDC}")

def print_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_lines = []
    report_lines.append("\n" + "="*50)
    report_lines.append(f" التقرير النهائي الشامل (AboElfadl Auto Scanner)")
    report_lines.append("="*50)
    report_lines.append(f" وقت التقرير: {timestamp}")
    report_lines.append("-" * 50)
    report_lines.append(f" {'الصيغة':<10} | {'العدد':<10}")
    report_lines.append("-" * 50)
    
    # ترتيب النتائج وعرضها
    for ext, count in TARGET_EXTENSIONS.items():
        report_lines.append(f" {ext:<10} | {count:<10}")
    
    report_lines.append("-" * 50)
    report_lines.append(f" إجمالي الملفات المفحوصة في الجهاز: {TOTAL_SCANNED_FILES}")
    report_lines.append("="*50)
    
    full_report = "\n".join(report_lines)
    print(Colors.GREEN + full_report + Colors.ENDC)
    
    with open("Full_Scan_Report.txt", "w", encoding="utf-8") as f:
        f.write(full_report)
    print(f"\n{Colors.BOLD}[+] تم حفظ التقرير في ملف: Full_Scan_Report.txt{Colors.ENDC}")

def main():
    clear_screen()
    print(f"{Colors.BOLD}{Colors.HEADER}--- أداة الفحص الشامل التلقائي ---{Colors.ENDC}")
    print("سيتم فحص جميع وحدات التخزين المتصلة بالجهاز الآن...")
    print("-" * 50)
    
    # الخطوة 1: جلب المسارات تلقائياً
    paths = get_drives_or_storage()
    
    if not paths:
        print(f"{Colors.FAIL}لم يتم العثور على وحدات تخزين!{Colors.ENDC}")
        return

    print(f"تم العثور على المسارات التالية: {paths}")
    
    # الخطوة 2: الفحص
    for path in paths:
        scan_path(path)
        
    # الخطوة 3: التقرير
    print_report()

if __name__ == "__main__":
    main()