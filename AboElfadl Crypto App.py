import sys
import subprocess
import os

# --- 1. قسم التثبيت التلقائي للمكاتب (Auto-Install Logic) ---
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"جاري تثبيت المكتبة المطلوبة: {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"تم تثبيت {package_name} بنجاح!")
        except Exception as e:
            print(f"فشل تثبيت {package_name}: {e}")

# التحقق من المكتبات وتثبيتها قبل بدء البرنامج
install_and_import("customtkinter")
install_and_import("cryptography")

# --- 2. استدعاء المكتبات بعد التأكد من وجودها ---
import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet

# --- 3. إعدادات البرنامج ---
# إعدادات المظهر العام للواجهة (ليلي واحترافي)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class AboElfadlCryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة الرئيسية
        self.title("AboElfadl - Code Encryptor & Decryptor")
        self.geometry("700x500")
        self.resizable(False, False)

        # متغير لتخزين مسار المفتاح والملف
        self.key = None
        self.file_path = None

        # --- التصميم (Layout) ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # العنوان الرئيسي
        self.lbl_title = ctk.CTkLabel(self, text="نظام تشفير وحماية الملفات البرمجية", 
                                      font=("Arial", 24, "bold"), text_color="#3B8ED0")
        self.lbl_title.grid(row=0, column=0, pady=20, sticky="ew")

        # نظام التبويبات (Tabs)
        self.tabview = ctk.CTkTabview(self, width=650, height=300)
        self.tabview.grid(row=1, column=0, padx=20, pady=10)
        
        self.tab_encrypt = self.tabview.add("تشفير (Encrypt)")
        self.tab_decrypt = self.tabview.add("فك التشفير (Decrypt)")

        # محتويات التبويبات
        self.setup_encrypt_tab()
        self.setup_decrypt_tab()

        # منطقة السجل (Logs)
        self.textbox_log = ctk.CTkTextbox(self, width=650, height=100, corner_radius=10)
        self.textbox_log.grid(row=2, column=0, padx=20, pady=20)
        self.log_message("تم تشغيل النظام. تم فحص المكتبات وتحديثها تلقائياً.")

    def setup_encrypt_tab(self):
        btn_gen_key = ctk.CTkButton(self.tab_encrypt, text="1. توليد مفتاح تشفير جديد (Generate Key)", 
                                    command=self.generate_key, fg_color="#D32F2F", hover_color="#B71C1C")
        btn_gen_key.pack(pady=15, padx=20, fill="x")

        btn_load_key = ctk.CTkButton(self.tab_encrypt, text="أو تحميل مفتاح موجود", 
                                     command=self.load_key)
        btn_load_key.pack(pady=5, padx=20, fill="x")

        btn_select_file = ctk.CTkButton(self.tab_encrypt, text="2. اختيار ملف الكود (Select File)", 
                                        command=self.select_file)
        btn_select_file.pack(pady=15, padx=20, fill="x")

        btn_action = ctk.CTkButton(self.tab_encrypt, text="3. تنفيذ التشفير الآن", 
                                   command=self.encrypt_file, fg_color="#388E3C", hover_color="#2E7D32")
        btn_action.pack(pady=15, padx=20, fill="x")

    def setup_decrypt_tab(self):
        btn_load_key = ctk.CTkButton(self.tab_decrypt, text="1. تحميل مفتاح فك التشفير (Load Key)", 
                                     command=self.load_key)
        btn_load_key.pack(pady=15, padx=20, fill="x")

        btn_select_file = ctk.CTkButton(self.tab_decrypt, text="2. اختيار الملف المشفر (.enc)", 
                                        command=self.select_file)
        btn_select_file.pack(pady=15, padx=20, fill="x")

        btn_action = ctk.CTkButton(self.tab_decrypt, text="3. استعادة الملف الأصلي", 
                                   command=self.decrypt_file, fg_color="#388E3C", hover_color="#2E7D32")
        btn_action.pack(pady=15, padx=20, fill="x")

    # --- الوظائف المنطقية (Logic) ---
    def log_message(self, message):
        self.textbox_log.insert("end", f">> {message}\n")
        self.textbox_log.see("end")

    def generate_key(self):
        try:
            self.key = Fernet.generate_key()
            file_path = filedialog.asksaveasfilename(defaultextension=".key", 
                                                     filetypes=[("Key Files", "*.key")],
                                                     title="حفظ مفتاح التشفير")
            if file_path:
                with open(file_path, "wb") as key_file:
                    key_file.write(self.key)
                self.log_message(f"تم توليد المفتاح: {os.path.basename(file_path)}")
                self.log_message("⚠️ احتفظ بهذا المفتاح جيداً!")
        except Exception as e:
            self.log_message(f"خطأ: {str(e)}")

    def load_key(self):
        file_path = filedialog.askopenfilename(filetypes=[("Key Files", "*.key")])
        if file_path:
            with open(file_path, "rb") as key_file:
                self.key = key_file.read()
            self.log_message("تم تحميل المفتاح بنجاح.")

    def select_file(self):
        self.file_path = filedialog.askopenfilename(title="اختر الملف")
        if self.file_path:
            self.log_message(f"تم تحديد: {os.path.basename(self.file_path)}")

    def encrypt_file(self):
        if not self.key or not self.file_path:
            messagebox.showerror("خطأ", "المفتاح أو الملف ناقص!")
            return
        try:
            f = Fernet(self.key)
            with open(self.file_path, "rb") as file:
                file_data = file.read()
            encrypted_data = f.encrypt(file_data)
            output_path = self.file_path + ".enc"
            with open(output_path, "wb") as file:
                file.write(encrypted_data)
            self.log_message(f"✅ تم التشفير: {os.path.basename(output_path)}")
            messagebox.showinfo("تم", "تم التشفير بنجاح.")
        except Exception as e:
            self.log_message(f"❌ خطأ: {str(e)}")

    def decrypt_file(self):
        if not self.key or not self.file_path:
            messagebox.showerror("خطأ", "المفتاح أو الملف ناقص!")
            return
        try:
            f = Fernet(self.key)
            with open(self.file_path, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
            output_path = self.file_path.replace(".enc", "")
            if output_path == self.file_path:
                output_path = "decrypted_" + os.path.basename(self.file_path)
            with open(output_path, "wb") as file:
                file.write(decrypted_data)
            self.log_message(f"✅ تم فك التشفير: {os.path.basename(output_path)}")
            messagebox.showinfo("تم", "تمت الاستعادة بنجاح.")
        except Exception as e:
            self.log_message(f"❌ خطأ في فك التشفير: {str(e)}")

if __name__ == "__main__":
    app = AboElfadlCryptoApp()
    app.mainloop()