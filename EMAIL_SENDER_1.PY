import customtkinter as ctk
import smtplib
import threading
import time
import os
from tkinter import filedialog, messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- إعداد المظهر ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class MarketingToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AboElfadl Media | Marketing Sender Pro v2.0")
        self.geometry("850x700") # زيادة الحجم قليلاً لاستيعاب الأزرار
        self.resizable(False, False)

        # متغيرات التشغيل
        self.email_list = []
        self.html_content = ""
        self.attachment_path = None # مسار ملف المرفقات
        self.running = False
        self.total_sent = 0
        self.total_failed = 0

        # --- العنوان ---
        self.header = ctk.CTkLabel(
            self, 
            text="📧 AboElfadl Marketing Sender", 
            font=("Segoe UI", 24, "bold"),
            text_color="#3B8ED0"
        )
        self.header.pack(pady=15)

        # --- (1) إعدادات المرسل (SMTP) ---
        self.frame_smtp = ctk.CTkFrame(self)
        self.frame_smtp.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.frame_smtp, text="بيانات المرسل (SMTP Config)", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.sender_email = ctk.CTkEntry(self.frame_smtp, placeholder_text="Email (Gmail)", width=300)
        self.sender_email.pack(pady=5)
        self.sender_email.insert(0, "iphone011012013@gmail.com") 

        self.sender_pass = ctk.CTkEntry(self.frame_smtp, placeholder_text="App Password", width=300, show="*")
        self.sender_pass.pack(pady=5)
        self.sender_pass.insert(0, "qrpf wkub heck bnbi")

        # --- (2) إعدادات الحملة (Campaign) ---
        self.frame_campaign = ctk.CTkFrame(self)
        self.frame_campaign.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_campaign, text="إعدادات الحملة الإعلانية والمرفقات", font=("Arial", 14, "bold")).pack(pady=5)

        # عنوان الرسالة
        self.subject_entry = ctk.CTkEntry(self.frame_campaign, placeholder_text="عنوان الرسالة (Subject Line)", width=450)
        self.subject_entry.pack(pady=5)

        # أزرار رفع الملفات
        self.files_frame = ctk.CTkFrame(self.frame_campaign, fg_color="transparent")
        self.files_frame.pack(pady=5)

        # زر رفع القائمة
        self.btn_load_emails = ctk.CTkButton(self.files_frame, text="📂 القائمة (.txt)", command=self.load_emails_file, width=120)
        self.btn_load_emails.pack(side="left", padx=5)

        # زر رفع التصميم
        self.btn_load_html = ctk.CTkButton(self.files_frame, text="🎨 التصميم (.html)", command=self.load_html_file, fg_color="#D35400", hover_color="#A04000", width=120)
        self.btn_load_html.pack(side="left", padx=5)

        # زر إرفاق ملف (الجديد)
        self.btn_attach_file = ctk.CTkButton(self.files_frame, text="📎 إرفاق ملف", command=self.select_attachment, fg_color="#5B2C6F", hover_color="#4A235A", width=120)
        self.btn_attach_file.pack(side="left", padx=5)

        # ملخص الملفات
        self.lbl_status_files = ctk.CTkLabel(self.frame_campaign, text="لم يتم اختيار ملفات...", text_color="gray", wraplength=700)
        self.lbl_status_files.pack(pady=5)

        # --- (3) التحكم والتشغيل ---
        self.frame_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_controls.pack(pady=5)

        self.delay_slider = ctk.CTkSlider(self.frame_controls, from_=2, to=30, number_of_steps=28, width=200)
        self.delay_slider.set(5)
        self.delay_slider.pack(side="left", padx=10)
        
        self.lbl_delay = ctk.CTkLabel(self.frame_controls, text="فواصل: 5 ث")
        self.lbl_delay.pack(side="left", padx=5)
        
        self.delay_slider.configure(command=lambda val: self.lbl_delay.configure(text=f"فواصل: {int(val)} ث"))

        self.start_btn = ctk.CTkButton(self.frame_controls, text="🚀 إرسال", command=self.start_thread, fg_color="green", hover_color="darkgreen", width=100)
        self.start_btn.pack(side="left", padx=20)

        self.stop_btn = ctk.CTkButton(self.frame_controls, text="🛑 إيقاف", command=self.stop_process, fg_color="red", hover_color="darkred", state="disabled", width=80)
        self.stop_btn.pack(side="left", padx=5)

        # --- السجل (Log) ---
        self.log_box = ctk.CTkTextbox(self, width=750, height=200, font=("Consolas", 12))
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def update_status_label(self):
        # دالة لتحديث نص الحالة بناء على الملفات المرفوعة
        status_text = ""
        if self.email_list: status_text += f"✅ قائمة: {len(self.email_list)} | "
        if self.html_content: status_text += "✅ HTML | "
        if self.attachment_path: status_text += f"📎 مرفق: {os.path.basename(self.attachment_path)}"
        
        if status_text == "": status_text = "لم يتم اختيار ملفات..."
        self.lbl_status_files.configure(text=status_text, text_color="lightgreen" if status_text else "gray")

    def load_emails_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.email_list = [line.strip() for line in f.readlines() if line.strip()]
            self.log(f"📂 تم تحميل القائمة: {len(self.email_list)} جهة اتصال.")
            self.update_status_label()

    def load_html_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.html_content = f.read()
            self.log("🎨 تم تحميل تصميم HTML.")
            self.update_status_label()

    def select_attachment(self):
        # دالة اختيار الملف المرفق
        file_path = filedialog.askopenfilename()
        if file_path:
            self.attachment_path = file_path
            self.log(f"📎 تم تحديد المرفق: {os.path.basename(file_path)}")
            self.update_status_label()

    def start_thread(self):
        if not self.email_list:
            messagebox.showwarning("تنبيه", "يجب رفع قائمة الإيميلات أولاً.")
            return
        if not self.subject_entry.get():
            messagebox.showwarning("تنبيه", "يجب كتابة عنوان للرسالة.")
            return
        
        if not self.running:
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            
            threading.Thread(target=self.process_sending, daemon=True).start()

    def stop_process(self):
        self.running = False
        self.log("⚠️ جاري الإيقاف...")

    def process_sending(self):
        sender = self.sender_email.get()
        password = self.sender_pass.get()
        subject = self.subject_entry.get()
        delay = int(self.delay_slider.get())

        self.log("🔄 جاري الاتصال بالسيرفر وتجهيز الملفات...")

        try:
            # تجهيز المرفق مرة واحدة (لتحسين الأداء)
            attachment_part = None
            if self.attachment_path:
                try:
                    with open(self.attachment_path, "rb") as attachment:
                        attachment_part = MIMEBase("application", "octet-stream")
                        attachment_part.set_payload(attachment.read())
                    encoders.encode_base64(attachment_part)
                    attachment_part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(self.attachment_path)}",
                    )
                except Exception as e:
                    self.log(f"❌ خطأ في قراءة المرفق: {e}")
                    self.reset_buttons()
                    return

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password.replace(" ", ""))
            self.log("✅ تم الاتصال. بدء الحملة...")

            for index, target_email in enumerate(self.email_list):
                if not self.running:
                    break

                msg = MIMEMultipart()
                msg['From'] = f"AboElfadl Media <{sender}>"
                msg['To'] = target_email
                msg['Subject'] = subject

                # 1. إضافة المحتوى (HTML أو نص)
                if self.html_content:
                    msg.attach(MIMEText(self.html_content, 'html', 'utf-8'))
                else:
                    msg.attach(MIMEText("This is a message from AboElfadl Media.", 'plain', 'utf-8'))

                # 2. إضافة المرفق (إذا وجد)
                if attachment_part:
                    # يجب نسخ الكائن لأن بعض السيرفرات تعدل الهيدر عند الإرسال
                    # لكن في بايثون يمكن إعادة استخدامه، للأمان سنقوم بإرفاقه مباشرة
                    msg.attach(attachment_part)

                try:
                    server.sendmail(sender, target_email, msg.as_string())
                    self.total_sent += 1
                    self.log(f"✅ ({index+1}/{len(self.email_list)}) تم الإرسال لـ: {target_email}")
                except Exception as e:
                    self.total_failed += 1
                    self.log(f"❌ فشل ({target_email}): {e}")

                time.sleep(delay)

            server.quit()
            self.log(f"\n🏁 النتيجة النهائية: ✅ {self.total_sent} | ❌ {self.total_failed}")

        except Exception as e:
            self.log(f"⛔ خطأ في الاتصال: {e}")

        self.reset_buttons()

    def reset_buttons(self):
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

if __name__ == "__main__":
    app = MarketingToolApp()
    app.mainloop()