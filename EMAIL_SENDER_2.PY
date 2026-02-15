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

        self.title("AboElfadl Media | Marketing Sender Pro v3.0")
        self.geometry("850x750")
        self.resizable(False, False)

        # متغيرات التشغيل
        self.email_list = []
        self.html_content = ""
        self.attachment_path = None
        self.running = False
        self.total_sent = 0
        self.total_failed = 0

        # --- (1) العنوان الرئيسي القابل للتعديل ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=10)
        
        # حقل إدخال العنوان الرئيسي (بدلاً من نص ثابت)
        self.app_title_entry = ctk.CTkEntry(
            self.header_frame, 
            font=("Segoe UI", 22, "bold"), 
            width=400, 
            fg_color="transparent", 
            border_width=0, 
            justify="center",
            text_color="#3B8ED0"
        )
        self.app_title_entry.pack()
        self.app_title_entry.insert(0, "AboElfadl Marketing Sender") # النص الافتراضي

        # --- (2) إعدادات المرسل والهوية ---
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.frame_config, text="إعدادات الهوية والاتصال", font=("Arial", 13, "bold")).pack(pady=5)
        
        # الصف الأول: الإيميل والباسورد
        self.row1 = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.row1.pack(pady=2)
        
        self.sender_email = ctk.CTkEntry(self.row1, placeholder_text="البريد (Gmail)", width=280)
        self.sender_email.pack(side="left", padx=5)
        self.sender_email.insert(0, "iphone011012013@gmail.com") 

        self.sender_pass = ctk.CTkEntry(self.row1, placeholder_text="كلمة مرور التطبيق", width=280, show="*")
        self.sender_pass.pack(side="left", padx=5)
        self.sender_pass.insert(0, "qrpf wkub heck bnbi")

        # الصف الثاني: اسم العرض (الجديد)
        self.row2 = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.row2.pack(pady=5)

        ctk.CTkLabel(self.row2, text="اسم المرسل (كما يظهر للعميل):").pack(side="left", padx=5)
        self.display_name_entry = ctk.CTkEntry(self.row2, placeholder_text="مثال: AboElfadl Support", width=300)
        self.display_name_entry.pack(side="left", padx=5)
        self.display_name_entry.insert(0, "AboElfadl Media")

        # --- (3) إعدادات المستلم (يدوي أو ملف) ---
        self.frame_target = ctk.CTkFrame(self)
        self.frame_target.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_target, text="تحديد المستلمين", font=("Arial", 13, "bold")).pack(pady=5)

        # -- خيار الإدخال اليدوي (الجديد) --
        self.manual_frame = ctk.CTkFrame(self.frame_target, fg_color="transparent")
        self.manual_frame.pack(pady=5)

        self.manual_email_entry = ctk.CTkEntry(self.manual_frame, placeholder_text="أدخل بريد مستلم واحد هنا...", width=350)
        self.manual_email_entry.pack(side="left", padx=5)

        # زر اللصق (Paste)
        self.btn_paste = ctk.CTkButton(self.manual_frame, text="📋 لصق", width=60, command=self.paste_from_clipboard, fg_color="#555", hover_color="#333")
        self.btn_paste.pack(side="left", padx=5)

        # -- خيار الملف --
        self.file_btn_frame = ctk.CTkFrame(self.frame_target, fg_color="transparent")
        self.file_btn_frame.pack(pady=5)
        
        self.btn_load_emails = ctk.CTkButton(self.file_btn_frame, text="📂 أو ارفع قائمة (.txt)", command=self.load_emails_file, width=200)
        self.btn_load_emails.pack()

        # حالة القائمة
        self.lbl_list_status = ctk.CTkLabel(self.frame_target, text="القائمة فارغة (سيتم الإرسال للإيميل اليدوي فقط)", text_color="gray", font=("Arial", 11))
        self.lbl_list_status.pack(pady=2)

        # --- (4) محتوى الرسالة والمرفقات ---
        self.frame_content = ctk.CTkFrame(self)
        self.frame_content.pack(pady=10, padx=20, fill="x")

        self.subject_entry = ctk.CTkEntry(self.frame_content, placeholder_text="عنوان الرسالة (Subject Line)", width=500)
        self.subject_entry.pack(pady=10)

        self.attach_frame = ctk.CTkFrame(self.frame_content, fg_color="transparent")
        self.attach_frame.pack(pady=5)

        self.btn_load_html = ctk.CTkButton(self.attach_frame, text="🎨 تصميم HTML", command=self.load_html_file, fg_color="#D35400", hover_color="#A04000")
        self.btn_load_html.pack(side="left", padx=10)

        self.btn_attach_file = ctk.CTkButton(self.attach_frame, text="📎 إرفاق ملف", command=self.select_attachment, fg_color="#5B2C6F", hover_color="#4A235A")
        self.btn_attach_file.pack(side="left", padx=10)

        self.lbl_files_status = ctk.CTkLabel(self.frame_content, text="", text_color="lightgreen", font=("Arial", 11))
        self.lbl_files_status.pack(pady=2)

        # --- التحكم ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=5)

        self.delay_slider = ctk.CTkSlider(self.controls_frame, from_=2, to=30, number_of_steps=28, width=200)
        self.delay_slider.set(5)
        self.delay_slider.pack(side="left", padx=10)
        self.lbl_delay = ctk.CTkLabel(self.controls_frame, text="فواصل: 5 ث")
        self.lbl_delay.pack(side="left")
        self.delay_slider.configure(command=lambda val: self.lbl_delay.configure(text=f"فواصل: {int(val)} ث"))

        self.start_btn = ctk.CTkButton(self.controls_frame, text="🚀 إرسال الآن", command=self.start_thread, fg_color="green", hover_color="darkgreen", width=120, height=35)
        self.start_btn.pack(side="left", padx=20)

        self.stop_btn = ctk.CTkButton(self.controls_frame, text="إيقاف", command=self.stop_process, fg_color="red", hover_color="darkred", state="disabled", width=60)
        self.stop_btn.pack(side="left", padx=5)

        # --- السجل ---
        self.log_box = ctk.CTkTextbox(self, width=800, height=150, font=("Consolas", 11))
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)

    # --- الوظائف ---
    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def paste_from_clipboard(self):
        try:
            # دالة لجلب النص من الحافظة ولصقه في الخانة اليدوية
            text = self.clipboard_get()
            self.manual_email_entry.delete(0, 'end')
            self.manual_email_entry.insert(0, text)
            self.log(f"📋 تم لصق: {text}")
        except:
            self.log("⚠️ الحافظة فارغة أو لا تحتوي على نص.")

    def load_emails_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.email_list = [line.strip() for line in f.readlines() if line.strip()]
            self.lbl_list_status.configure(text=f"✅ تم تحميل القائمة: {len(self.email_list)} جهة اتصال")
            self.log(f"📂 تم تحميل القائمة: {len(self.email_list)} مستلم.")

    def load_html_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.html_content = f.read()
            self.lbl_files_status.configure(text=self.lbl_files_status.cget("text") + " [HTML Loaded] ")
            self.log("🎨 تم تحميل HTML.")

    def select_attachment(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.attachment_path = file_path
            self.lbl_files_status.configure(text=self.lbl_files_status.cget("text") + f" [ملف: {os.path.basename(file_path)}] ")
            self.log(f"📎 مرفق: {os.path.basename(file_path)}")

    def start_thread(self):
        # التحقق من وجود مستلم (إما في القائمة أو يدوي)
        manual_target = self.manual_email_entry.get().strip()
        
        if not self.email_list and not manual_target:
            messagebox.showwarning("تنبيه", "يجب تحديد مستلم (اكتب إيميل يدوياً أو ارفع قائمة).")
            return
        
        if not self.subject_entry.get():
            messagebox.showwarning("تنبيه", "عنوان الرسالة مطلوب.")
            return

        if not self.running:
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            threading.Thread(target=self.process_sending, daemon=True).start()

    def stop_process(self):
        self.running = False
        self.log("⚠️ إيقاف...")

    def process_sending(self):
        sender_addr = self.sender_email.get()
        sender_pass = self.sender_pass.get()
        display_name = self.display_name_entry.get() # الاسم الجديد
        subject = self.subject_entry.get()
        delay = int(self.delay_slider.get())
        
        # تجميع قائمة المستلمين (القائمة + اليدوي)
        targets = self.email_list.copy()
        manual_target = self.manual_email_entry.get().strip()
        if manual_target:
            targets.append(manual_target)
            # إزالة التكرار إن وجد
            targets = list(set(targets))

        self.log(f"🔄 جاري البدء... العدد الكلي: {len(targets)}")

        try:
            # تجهيز المرفق
            attachment_part = None
            if self.attachment_path:
                try:
                    with open(self.attachment_path, "rb") as f:
                        attachment_part = MIMEBase("application", "octet-stream")
                        attachment_part.set_payload(f.read())
                    encoders.encode_base64(attachment_part)
                    attachment_part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.attachment_path)}")
                except Exception as e:
                    self.log(f"❌ خطأ في المرفق: {e}")
                    self.reset_buttons()
                    return

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_addr, sender_pass.replace(" ", ""))
            self.log("✅ تم الاتصال بالسيرفر.")

            for i, target in enumerate(targets):
                if not self.running: break

                msg = MIMEMultipart()
                # هنا يتم وضع اسم العرض المخصص
                msg['From'] = f"{display_name} <{sender_addr}>"
                msg['To'] = target
                msg['Subject'] = subject

                if self.html_content:
                    msg.attach(MIMEText(self.html_content, 'html', 'utf-8'))
                else:
                    msg.attach(MIMEText("رسالة تجريبية من النظام.", 'plain', 'utf-8'))

                if attachment_part:
                    msg.attach(attachment_part)

                try:
                    server.sendmail(sender_addr, target, msg.as_string())
                    self.total_sent += 1
                    self.log(f"📤 ({i+1}/{len(targets)}) تم الإرسال لـ: {target}")
                except Exception as e:
                    self.total_failed += 1
                    self.log(f"❌ خطأ مع {target}: {e}")

                time.sleep(delay)

            server.quit()
            self.log(f"🏁 تم الانتهاء. نجاح: {self.total_sent} | فشل: {self.total_failed}")

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