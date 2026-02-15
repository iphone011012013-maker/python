import sys
import subprocess
import time
import datetime
import threading
import winsound
import requests  # مكتبة الإرسال عبر الإنترنت
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QGroupBox)
from PyQt6.QtCore import pyqtSignal, QObject, Qt

# --- بيانات التيليجرام الخاصة بك ---
TELEGRAM_TOKEN = "7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0"
CHAT_ID = "1431886140"

class Signaller(QObject):
    log_update = pyqtSignal(str)
    device_update = pyqtSignal(str)

class AboElfadlDiagnosticApp(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = Signaller()
        self.signals.log_update.connect(self.append_log)
        self.signals.device_update.connect(self.update_details)
        self.current_devices = set()
        self.monitoring = True
        
        self.initUI()
        
        # رسالة ترحيبية عند تشغيل البرنامج
        self.send_telegram_message("🚀 تم تشغيل نظام AboElfadl Security Scanner بنجاح.")
        
        self.monitor_thread = threading.Thread(target=self.monitor_usb_ports)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def initUI(self):
        self.setWindowTitle('AboElfadl Security - Remote Monitor')
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("""
            QWidget { background-color: #1a1a1a; color: #00ff00; font-family: 'Consolas'; }
            QGroupBox { border: 1px solid #00ff00; margin-top: 10px; }
            QGroupBox::title { color: white; }
            QTextEdit { background-color: black; border: 1px solid #333; color: #00ff00; }
            QPushButton { background-color: #004400; color: white; border: 1px solid #00ff00; padding: 10px; }
            QPushButton:hover { background-color: #006600; }
        """)

        layout = QVBoxLayout()

        header = QLabel("📡 نظام المراقبة والإرسال التلقائي")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(header)

        self.details_box = QGroupBox("تقرير الجهاز (يتم إرساله للتيليجرام)")
        details_layout = QVBoxLayout()
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)
        details_layout.addWidget(self.details_area)
        self.details_box.setLayout(details_layout)
        layout.addWidget(self.details_box)

        self.log_box = QGroupBox("سجل الأحداث")
        log_layout = QVBoxLayout()
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        self.log_box.setLayout(log_layout)
        layout.addWidget(self.log_box)

        self.btn_manual = QPushButton("إجراء فحص يدوي وإرسال تقرير")
        self.btn_manual.clicked.connect(self.run_deep_scan)
        layout.addWidget(self.btn_manual)

        self.setLayout(layout)

    # --- وظائف التيليجرام ---
    def send_telegram_message(self, message):
        """إرسال رسالة في الخلفية حتى لا يهنق البرنامج"""
        def _send():
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                payload = {
                    "chat_id": CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown" # لتنسيق النص بشكل جميل
                }
                requests.post(url, data=payload)
            except Exception as e:
                self.signals.log_update.emit(f"❌ فشل إرسال التيليجرام: {e}")

        # تشغيل الإرسال في Thread منفصل
        t = threading.Thread(target=_send)
        t.start()

    # --- وظائف النظام والأدوات ---
    def run_adb_command(self, command):
        try:
            full_cmd = f"adb {command}"
            result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
            return result.strip()
        except:
            return None

    def get_connected_devices(self):
        output = self.run_adb_command("devices")
        devices = []
        if output:
            lines = output.split('\n')
            for line in lines[1:]:
                if "\tdevice" in line:
                    devices.append(line.split('\t')[0])
        return devices

    def monitor_usb_ports(self):
        while self.monitoring:
            devices = set(self.get_connected_devices())
            
            # عند توصيل جهاز جديد
            new_devices = devices - self.current_devices
            for dev in new_devices:
                alert_msg = f"⚠️ *تنبيه أمني!* \nتم توصيل جهاز جديد باللابتوب.\nID: `{dev}`"
                self.log_event(f"تم توصيل جهاز: {dev}")
                self.send_telegram_message(alert_msg) # إرسال تنبيه فوري
                self.alert_sound(connect=True)
                self.perform_scan(dev) # بدء الفحص والإرسال

            # عند فصل جهاز
            removed_devices = self.current_devices - devices
            for dev in removed_devices:
                self.log_event(f"تم فصل الجهاز: {dev}")
                self.send_telegram_message(f"🔌 تم فصل الجهاز: `{dev}`")
                self.alert_sound(connect=False)

            self.current_devices = devices
            time.sleep(2)

    def alert_sound(self, connect=True):
        try:
            if connect: winsound.Beep(1000, 200)
            else: winsound.Beep(500, 200)
        except: pass

    def log_event(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.signals.log_update.emit(f"[{timestamp}] {message}")

    def append_log(self, text):
        self.log_area.append(text)

    def update_details(self, text):
        self.details_area.setText(text)

    def run_deep_scan(self):
        devices = self.get_connected_devices()
        if not devices:
            self.update_details("❌ لا يوجد أجهزة.")
            return
        for dev in devices:
            self.perform_scan(dev)

    def perform_scan(self, device_id):
        self.log_event(f"جاري فحص الجهاز {device_id}...")
        
        # جمع البيانات
        model = self.run_adb_command(f"-s {device_id} shell getprop ro.product.model")
        brand = self.run_adb_command(f"-s {device_id} shell getprop ro.product.brand")
        android_ver = self.run_adb_command(f"-s {device_id} shell getprop ro.build.version.release")
        battery = self.run_adb_command(f"-s {device_id} shell dumpsys battery | grep level")
        
        # تنسيق التقرير للتيليجرام
        report = f"""
🕵️‍♂️ *تقرير فحص جديد - AboElfadl Scanner*
--------------------------------
📱 *الجهاز:* {brand} {model}
🤖 *أندرويد:* {android_ver}
🔋 *البطارية:* {battery.strip() if battery else 'N/A'}
🆔 *الرقم التسلسلي:* `{device_id}`

⏳ *وقت الفحص:* {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        # تحديث الواجهة
        self.signals.device_update.emit(report)
        
        # إرسال التقرير للتيليجرام
        self.send_telegram_message(report)
        self.log_event("✅ تم إرسال التقرير للتيليجرام.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AboElfadlDiagnosticApp()
    ex.show()
    sys.exit(app.exec())