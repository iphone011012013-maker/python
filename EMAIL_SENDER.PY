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
ctk.set_default_color_theme("blue")

class MarketingToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AboElfadl Media | Marketing Sender Pro v7.0") # اسم البرنامج كمنتج
        self.geometry("700x600") 
        self.resizable(True, True) 

        # متغيرات التشغيل
        self.file_email_list = [] 
        self.html_content = ""
        self.attachment_path = None
        self.running = False
        self.total_sent = 0
        self.total_failed = 0

        # === الإطار الرئيسي القابل للتمرير ===
        self.main_scroll = ctk.CTkScrollableFrame(self, width=660, height=580)
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- (1) عنوان الحملة ---
        self.header_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.header_frame.pack(pady=5)
        
        # تركنا اسم البرنامج الافتراضي، لكن يمكن للمستخدم تغييره
        self.app_title_entry = ctk.CTkEntry(
            self.header_frame, 
            font=("Segoe UI", 22, "bold"), 
            width=400, 
            fg_color="transparent", 
            border_width=0, 
            justify="center",
            text_color="#3B8ED0",
            placeholder_text="اسم الحملة التسويقية"
        )
        self.app_title_entry.pack()
        self.app_title_entry.insert(0, "Email Marketing Campaign") # اسم افتراضي عام

        # --- (2) إعدادات هوية المستخدم (فارغة الآن) ---
        self.frame_config = ctk.CTkFrame(self.main_scroll)
        self.frame_config.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.frame_config, text="إعدادات الهوية (بياناتك)", font=("Arial", 12, "bold")).pack(pady=2)
        
        self.row1 = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.row1.pack(pady=2)
        
        # خانة الإيميل (فارغة)
        self.sender_email = ctk.CTkEntry(self.row1, placeholder_text="بريدك الإلكتروني (Gmail)", width=220)
        self.sender_email.pack(side="left", padx=5)

        # خانة الباسورد (فارغة)
        self.sender_pass = ctk.CTkEntry(self.row1, placeholder_text="كلمة مرور التطبيق (App Password)", width=220, show="*")
        self.sender_pass.pack(side="left", padx=5)

        self.row2 = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.row2.pack(pady=5)
        ctk.CTkLabel(self.row2, text="اسم المرسل:").pack(side="left", padx=5)
        
        # خانة اسم العرض (فارغة)
        self.display_name_entry = ctk.CTkEntry(self.row2, placeholder_text="اسم شركتك أو اسمك", width=250)
        self.display_name_entry.pack(side="left", padx=5)

        # --- (3) المستلمون ---
        self.frame_target = ctk.CTkFrame(self.main_scroll)
        self.frame_target.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.frame_target, text="قائمة المستلمين (العملاء)", font=("Arial", 12, "bold")).pack(pady=2)

        # صندوق الإدخال (فارغ)
        self.manual_emails_box = ctk.CTkTextbox(self.frame_target, height=100, width=500, border_width=1, border_color="gray")
        self.manual_emails_box.pack(pady=5)
        # وضعنا نص توضيحي يختفي عند الكتابة (Placeholder Logic بسيط)
        self.manual_emails_box.insert("0.0", "example@gmail.com\nclient@company.com")

        self.btns_frame = ctk.CTkFrame(self.frame_target, fg_color="transparent")
        self.btns_frame.pack(pady=2)

        self.btn_paste = ctk.CTkButton(self.btns_frame, text="📋 لصق القائمة", width=140, command=self.paste_from_clipboard, fg_color="#444", hover_color="#222")
        self.btn_paste.pack(side="left", padx=10)

        self.btn_load_file = ctk.CTkButton(self.btns_frame, text="📂 رفع ملف txt", width=140, command=self.load_emails_file)
        self.btn_load_file.pack(side="left", padx=10)

        self.lbl_list_status = ctk.CTkLabel(self.frame_target, text="لم يتم رفع ملف", text_color="gray", font=("Arial", 10))
        self.lbl_list_status.pack(pady=2)

        # --- (4) المحتوى ---
        self.frame_content = ctk.CTkFrame(self.main_scroll)
        self.frame_content.pack(pady=5, padx=10, fill="x")

        self.subject_entry = ctk.CTkEntry(self.frame_content, placeholder_text="عنوان الرسالة (Subject Line)", width=450)
        self.subject_entry.pack(pady=5)

        ctk.CTkLabel(self.frame_content, text="نص الرسالة (أو استخدم HTML للتصميم):", font=("Arial", 11)).pack(anchor="w", padx=30)
        self.body_text_box = ctk.CTkTextbox(self.frame_content, height=80, width=500)
        self.body_text_box.pack(pady=5)

        self.attach_frame = ctk.CTkFrame(self.frame_content, fg_color="transparent")
        self.attach_frame.pack(pady=5)

        self.btn_load_html = ctk.CTkButton(self.attach_frame, text="🎨 رفع تصميم HTML", command=self.load_html_file, fg_color="#D35400", hover_color="#A04000", width=140)
        self.btn_load_html.pack(side="left", padx=10)

        self.btn_attach_file = ctk.CTkButton(self.attach_frame, text="📎 إرفاق ملف", command=self.select_attachment, fg_color="#5B2C6F", hover_color="#4A235A", width=140)
        self.btn_attach_file.pack(side="left", padx=10)

        self.lbl_files_status = ctk.CTkLabel(self.frame_content, text="", text_color="lightgreen", font=("Arial", 10))
        self.lbl_files_status.pack(pady=2)

        # --- التحكم ---
        self.controls_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.controls_frame.pack(pady=5)

        self.delay_slider = ctk.CTkSlider(self.controls_frame, from_=2, to=30, number_of_steps=28, width=200)
        self.delay_slider.set(5)
        self.delay_slider.pack(side="left", padx=10)
        self.lbl_delay = ctk.CTkLabel(self.controls_frame, text="فواصل: 5 ث")
        self.lbl_delay.pack(side="left")
        self.delay_slider.configure(command=lambda val: self.lbl_delay.configure(text=f"فواصل: {int(val)} ث"))

        self.start_btn = ctk.CTkButton(self.controls_frame, text="🚀 إرسال الآن", command=self.start_thread, fg_color="green", hover_color="darkgreen", width=120, height=35)
        self.start_btn.pack(side="left", padx=20)

        self.stop_btn = ctk.CTkButton(self.controls_frame, text="إيقاف", command=self.stop_process, fg_color="red", hover_color="darkred", state="disabled", width=70)
        self.stop_btn.pack(side="left", padx=5)

        # --- السجل ---
        self.log_label = ctk.CTkLabel(self.main_scroll, text="سجل العمليات (Log):", anchor="w")
        self.log_label.pack(fill="x", padx=20, pady=(5, 0))

        self.log_box = ctk.CTkTextbox(self.main_scroll, width=600, height=150, font=("Consolas", 10))
        self.log_box.pack(pady=5, padx=20, fill="both", expand=True)

    # --- الوظائف ---
    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def paste_from_clipboard(self):
        try:
            text = self.clipboard_get()
            self.manual_emails_box.insert("end", "\n" + text)
            self.log(f"📋 تم لصق نصوص من الحافظة.")
        except:
            self.log("⚠️ الحافظة فارغة.")

    def load_emails_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.file_email_list = [line.strip() for line in f.readlines() if line.strip()]
            self.lbl_list_status.configure(text=f"✅ إيميلات من الملف: {len(self.file_email_list)}")
            self.log(f"📂 تم تحميل الملف: {len(self.file_email_list)} عنوان.")

    def load_html_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.html_content = f.read()
            self.lbl_files_status.configure(text=self.lbl_files_status.cget("text") + " [HTML Loaded] ")
            self.log("🎨 تم تحميل تصميم HTML.")

    def select_attachment(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.attachment_path = file_path
            self.lbl_files_status.configure(text=self.lbl_files_status.cget("text") + f" [ملف: {os.path.basename(file_path)}] ")
            self.log(f"📎 مرفق: {os.path.basename(file_path)}")

    def get_all_recipients(self):
        raw_text = self.manual_emails_box.get("0.0", "end")
        processed_text = raw_text.replace(",", "\n")
        # تنظيف القائمة من النص التوضيحي إذا نسيه المستخدم
        manual_list = []
        for line in processed_text.split("\n"):
            line = line.strip()
            if line and "@" in line and "example" not in line: # تجاهل المثال
                manual_list.append(line)
                
        all_emails = list(set(manual_list + self.file_email_list))
        return all_emails

    def start_thread(self):
        # التحقق من البيانات المدخلة
        if not self.sender_email.get() or not self.sender_pass.get():
             messagebox.showwarning("تنبيه", "يجب إدخال البريد الإلكتروني وكلمة المرور الخاصة بالمرسل.")
             return

        recipients = self.get_all_recipients()
        
        if not recipients:
            messagebox.showwarning("تنبيه", "لا يوجد مستلمين صالحين!")
            return
        
        if not self.subject_entry.get():
            messagebox.showwarning("تنبيه", "عنوان الرسالة مطلوب.")
            return

        if not self.running:
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            threading.Thread(target=self.process_sending, args=(recipients,), daemon=True).start()

    def stop_process(self):
        self.running = False
        self.log("⚠️ تم طلب الإيقاف...")

    def process_sending(self, targets):
        sender_addr = self.sender_email.get()
        sender_pass = self.sender_pass.get()
        display_name = self.display_name_entry.get()
        if not display_name: display_name = "Email Sender" # اسم احتياطي

        subject = self.subject_entry.get()
        body_text = self.body_text_box.get("0.0", "end").strip()
        delay = int(self.delay_slider.get())
        
        self.log(f"🔄 بدء الحملة.. المرسل: {display_name}")

        try:
            attachment_part = None
            if self.attachment_path:
                try:
                    with open(self.attachment_path, "rb") as f:
                        attachment_part = MIMEBase("application", "octet-stream")
                        attachment_part.set_payload(f.read())
                    encoders.encode_base64(attachment_part)
                    attachment_part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.attachment_path)}")
                except Exception as e:
                    self.log(f"❌ خطأ المرفق: {e}")
                    self.reset_buttons()
                    return

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            try:
                server.login(sender_addr, sender_pass.replace(" ", ""))
                self.log("✅ تم تسجيل الدخول بنجاح.")
            except Exception as login_err:
                 self.log(f"⛔ فشل تسجيل الدخول: {login_err}")
                 self.reset_buttons()
                 return

            for i, target in enumerate(targets):
                if not self.running: break

                msg = MIMEMultipart()
                msg['From'] = f"{display_name} <{sender_addr}>"
                msg['To'] = target
                msg['Subject'] = subject

                if self.html_content:
                    msg.attach(MIMEText(self.html_content, 'html', 'utf-8'))
                elif body_text:
                    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
                else:
                    msg.attach(MIMEText("", 'plain', 'utf-8'))

                if attachment_part:
                    msg.attach(attachment_part)

                try:
                    server.sendmail(sender_addr, target, msg.as_string())
                    self.total_sent += 1
                    self.log(f"📤 ({i+1}/{len(targets)}) تم الإرسال: {target}")
                except Exception as e:
                    self.total_failed += 1
                    self.log(f"❌ فشل {target}: {e}")

                time.sleep(delay)

            server.quit()
            self.log(f"🏁 انتهت الحملة. نجاح: {self.total_sent} | فشل: {self.total_failed}")

        except Exception as e:
            self.log(f"⛔ خطأ اتصال: {e}")

        self.reset_buttons()

    def reset_buttons(self):
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

if __name__ == "__main__":
    app = MarketingToolApp()
    app.mainloop()