import subprocess
import re
import time
import requests
import sys

# --- إعدادات تيليجرام (AboElfadl Config) ---
BOT_TOKEN = "8060685956:AAFHXTc20IE9uigl8_ESIJ9mQ04l7lgCtTA"
CHAT_ID = "1431886140"

# متغير لتخزين التقرير
report_buffer = ""

def log(text):
    """دالة لتجميع التقرير بدلاً من طباعته فقط"""
    global report_buffer
    print(text) # طباعة في الشاشة للمراقبة
    # إزالة أكواد الألوان من النص المرسل لتيليجرام لكي لا تشوه الرسالة
    clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
    report_buffer += clean_text + "\n"

def send_telegram_message(message):
    """إرسال التقرير إلى تيليجرام"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML" # لتنسيق الخط العريض
        }
        requests.post(url, data=data)
        print("\n✅ تم إرسال التقرير إلى تيليجرام بنجاح!")
    except Exception as e:
        print(f"\n❌ فشل في إرسال الرسالة: {e}")

# --- دوال ADB (معدلة للتسجيل في التقرير) ---
def run_adb_command(command):
    try:
        full_cmd = f"adb {command}" if not command.startswith("adb") else command
        # Timeout لمنع التعليق
        result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT, timeout=10).decode("utf-8")
        return result.strip()
    except:
        return None

def collect_full_report():
    global report_buffer
    report_buffer = "" # تصفير التقرير
    
    log("<b>🚀 تقرير فحص جهاز جديد (AboElfadl Tool)</b>")
    log("-----------------------------------------")

    # 1. النظام
    model = run_adb_command("shell getprop ro.product.model")
    brand = run_adb_command("shell getprop ro.product.brand")
    android_ver = run_adb_command("shell getprop ro.build.version.release")
    log(f"📱 <b>الجهاز:</b> {brand} {model}")
    log(f"🤖 <b>أندرويد:</b> {android_ver}")

    # 2. البطارية
    batt_info = run_adb_command("shell dumpsys battery")
    if batt_info:
        level = re.search(r"level: (\d+)", batt_info)
        health = re.search(r"health: (\d+)", batt_info)
        status = re.search(r"status: (\d+)", batt_info)
        
        l_val = level.group(1) if level else "??"
        
        # تفسير الصحة
        h_val = health.group(1) if health else "1"
        health_status = "Good ✅" if h_val == '2' else "Weak/Bad ⚠️"
        
        # تفسير الحالة
        s_val = status.group(1) if status else "1"
        charging_state = "🔌 يشحن" if s_val == '2' else "🔋 تفريغ"

        log(f"\n🔋 <b>البطارية:</b> {l_val}% ({charging_state})")
        log(f"❤️ <b>الحالة:</b> {health_status}")

    # 3. التخزين
    df_data = run_adb_command("shell df -h /data")
    if df_data:
        lines = df_data.splitlines()
        if len(lines) > 1:
            parts = lines[1].split()
            log(f"\n💾 <b>التخزين:</b> ممتلئ بنسبة {parts[-2]}")
            log(f"   (متاح {parts[2]} من أصل {parts[0]})")

    # 4. الشاشة
    res = run_adb_command("shell wm size")
    if res:
        size = res.split(":")[-1].strip()
        log(f"🖥️ <b>الشاشة:</b> {size}")

    # 5. الشبكة
    carrier = run_adb_command("shell getprop gsm.operator.alpha")
    wifi = run_adb_command("shell dumpsys wifi | grep 'SSID'")
    if carrier: log(f"\n📡 <b>SIM:</b> {carrier}")
    if wifi:
        ssid_match = re.search(r'SSID: "([^"]+)"', wifi)
        ssid = ssid_match.group(1) if ssid_match else "Unknown"
        log(f"🌐 <b>WiFi:</b> {ssid}")

    # 6. الروت (الأمن)
    su = run_adb_command("shell which su")
    root_status = "⚠️ ROOTED" if su else "✅ Safe (No Root)"
    log(f"\n🛡️ <b>الحماية:</b> {root_status}")
    
    log("-----------------------------------------")
    log(f"⏰ <b>وقت الفحص:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return report_buffer

# --- حلقة المراقبة (The Watchdog) ---
def monitor_usb_ports():
    print("👀 جاري مراقبة المنافذ... بانتظار توصيل هاتف...")
    print("   (اضغط Ctrl+C للإيقاف)")
    
    device_connected = False
    
    while True:
        try:
            # فحص قائمة الأجهزة
            devices_output = run_adb_command("devices")
            # تنظيف القائمة (إزالة السطر الأول List of devices attached)
            lines = [line for line in devices_output.splitlines() if line.strip() and "List of" not in line]
            
            # هل يوجد جهاز "device" (وليس offline أو unauthorized)
            current_devices = [line for line in lines if "\tdevice" in line]
            
            if current_devices:
                if not device_connected:
                    # جهاز جديد تم توصيله للتو!
                    print("\n🚀 تم اكتشاف جهاز جديد! جاري الفحص...")
                    report = collect_full_report()
                    
                    # إرسال التقرير
                    send_telegram_message(report)
                    
                    # محاولة التقاط صورة سريعة (اختياري)
                    # run_adb_command("shell input keyevent 27") 
                    
                    device_connected = True
            else:
                if device_connected:
                    print("\n🔌 تم فصل الجهاز. العودة لوضع المراقبة...")
                    device_connected = False
            
            time.sleep(3) # فحص كل 3 ثواني
            
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف البرنامج.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # تشغيل السيرفر الداخلي للـ ADB لضمان الاستقرار
    subprocess.run(["adb", "start-server"], stdout=subprocess.DEVNULL)
    monitor_usb_ports()