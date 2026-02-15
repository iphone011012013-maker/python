import os
import sys
import subprocess
from kivy.core.text import LabelBase

# --- تثبيت المكاتب الناقصة تلقائياً ---
def install(package):
    try:
        __import__(package)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except:
            pass

install("kivy")
install("kivymd")
install("cryptography")
install("arabic_reshaper")
install("bidi")

# --- الاستيراد ---
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from cryptography.fernet import Fernet
from kivy.utils import platform
from kivy.properties import StringProperty # إضافة هامة
import arabic_reshaper
from bidi.algorithm import get_display

# --- دالة تعريب النصوص ---
def ar(text):
    try:
        if not text: return ""
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text

# --- التصميم (تم تعديله لاستخدام متغير للخط بدلاً من اسم ثابت) ---
KV = '''
MDBoxLayout:
    orientation: 'vertical'
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDTopAppBar:
        title: app.convert("AboElfadl Cipher")
        left_action_items: [["shield-lock", lambda x: app.show_info()]]
        right_action_items: [["folder", lambda x: app.file_manager_open()]]
        elevation: 4
        md_bg_color: 0.8, 0, 0, 1

    MDBottomNavigation:
        panel_color: 0.15, 0.15, 0.15, 1
        selected_color_background: 0.8, 0, 0, 0.2
        text_color_active: 0.8, 0, 0, 1

        MDBottomNavigationItem:
            name: 'screen1'
            text: app.convert('تشفير/فك')
            icon: 'lock'

            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(20)
                
                MDLabel:
                    id: lbl_file
                    text: app.convert("لم يتم اختيار ملف")
                    halign: "center"
                    theme_text_color: "Error"
                    font_style: "H6"
                    font_name: app.font_name  # استخدام المتغير الذكي

                MDRaisedButton:
                    text: app.convert("1. اختر الملف")
                    icon: "folder-open"
                    pos_hint: {"center_x": .5}
                    md_bg_color: 0.2, 0.2, 0.2, 1
                    font_name: app.font_name
                    on_release: app.file_manager_open()

                MDTextField:
                    id: key_field
                    hint_text: app.convert("أدخل مفتاح التشفير هنا")
                    mode: "rectangle"
                    multiline: False
                    icon_right: "key"
                    font_name: app.font_name
                    font_name_hint_text: app.font_name

                MDBoxLayout:
                    spacing: dp(10)
                    adaptive_height: True
                    pos_hint: {"center_x": .5}

                    MDRaisedButton:
                        text: app.convert("توليد مفتاح")
                        md_bg_color: 0.8, 0.5, 0, 1
                        font_name: app.font_name
                        on_release: app.generate_key()

                    MDRaisedButton:
                        text: app.convert("نسخ المفتاح")
                        font_name: app.font_name
                        on_release: app.copy_key()

                MDBoxLayout:
                    spacing: dp(10)
                    adaptive_height: True
                    pos_hint: {"center_x": .5}

                    MDRaisedButton:
                        text: app.convert("🔒 تشفير")
                        md_bg_color: 0.8, 0, 0, 1
                        font_name: app.font_name
                        font_size: "18sp"
                        on_release: app.encrypt_file()

                    MDRaisedButton:
                        text: app.convert("🔓 فك تشفير")
                        md_bg_color: 0, 0.6, 0, 1
                        font_name: app.font_name
                        font_size: "18sp"
                        on_release: app.decrypt_file()

        MDBottomNavigationItem:
            name: 'screen2'
            text: app.convert('تغيير المفتاح')
            icon: 'key-change'

            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(20)

                MDLabel:
                    text: app.convert("إعادة تشفير ملف بمفتاح جديد")
                    halign: "center"
                    font_style: "H5"
                    theme_text_color: "Primary"
                    font_name: app.font_name

                MDTextField:
                    id: old_key_field
                    hint_text: app.convert("المفتاح القديم")
                    mode: "rectangle"
                    font_name: app.font_name
                    font_name_hint_text: app.font_name

                MDRaisedButton:
                    text: app.convert("توليد مفتاح جديد وتغيير التشفير")
                    md_bg_color: 0.8, 0, 0, 1
                    pos_hint: {"center_x": .5}
                    font_name: app.font_name
                    on_release: app.change_file_key()
'''

class AboElfadlCipherApp(MDApp):
    # متغير لتحديد اسم الخط المستخدم ديناميكياً
    font_name = StringProperty("Roboto") 

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        
        # --- فحص ذكي للخط لمنع الإغلاق ---
        if os.path.exists("font.ttf"):
            self.font_name = "font.ttf"
        else:
            print("تحذير: ملف font.ttf غير موجود! سيتم استخدام الخط الافتراضي.")
            # استخدام خط افتراضي موجود في النظام لتجنب الإغلاق
            self.font_name = "Arial" if platform != 'android' else "Roboto"

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.selected_file_path = None
        return Builder.load_string(KV)

    def convert(self, text):
        return ar(text)

    # --- إدارة الملفات ---
    def file_manager_open(self):
        path = os.path.expanduser("~")
        if platform == 'android':
            path = "/storage/emulated/0/"
        self.file_manager.show(path)

    def select_path(self, path):
        self.exit_manager()
        self.selected_file_path = path
        self.root.ids.lbl_file.text = self.convert(f"الملف: {os.path.basename(path)}")
        self.root.ids.lbl_file.theme_text_color = "Custom"
        self.root.ids.lbl_file.text_color = (0, 1, 0, 1)
        toast(self.convert(f"تم تحديد: {os.path.basename(path)}"))

    def exit_manager(self, *args):
        self.file_manager.close()

    # --- منطق التشفير ---
    def generate_key(self):
        try:
            key = Fernet.generate_key()
            self.root.ids.key_field.text = key.decode()
            toast(self.convert("تم توليد مفتاح جديد"))
        except Exception as e:
            toast(str(e))

    def copy_key(self):
        from kivy.core.clipboard import Clipboard
        key = self.root.ids.key_field.text
        if key:
            Clipboard.copy(key)
            toast(self.convert("تم نسخ المفتاح"))
        else:
            toast(self.convert("لا يوجد مفتاح"))

    def encrypt_file(self):
        path = self.selected_file_path
        key = self.root.ids.key_field.text.encode()

        if not path or not key:
            toast(self.convert("اختر ملفاً وتأكد من وجود مفتاح!"))
            return

        try:
            f = Fernet(key)
            with open(path, "rb") as file:
                file_data = file.read()
            
            encrypted_data = f.encrypt(file_data)
            
            output_path = path + ".aboelfadl"
            with open(output_path, "wb") as file:
                file.write(encrypted_data)
            
            toast(self.convert("تم التشفير بنجاح"))
        except Exception as e:
            toast(f"Error: {str(e)}")

    def decrypt_file(self):
        path = self.selected_file_path
        key = self.root.ids.key_field.text.encode()

        if not path or not key:
            toast(self.convert("خطأ في البيانات"))
            return

        try:
            f = Fernet(key)
            with open(path, "rb") as file:
                encrypted_data = file.read()
            
            decrypted_data = f.decrypt(encrypted_data)
            
            output_path = path.replace(".aboelfadl", "")
            if output_path == path:
                 output_path += ".decrypted"

            with open(output_path, "wb") as file:
                file.write(decrypted_data)
                
            toast(self.convert("تم فك التشفير بنجاح!"))
        except Exception as e:
            toast(self.convert("المفتاح خطأ أو الملف تالف!"))

    def change_file_key(self):
        path = self.selected_file_path
        old_key = self.root.ids.old_key_field.text.encode()
        
        if not path or not old_key:
            toast(self.convert("حدد الملف وأدخل المفتاح القديم"))
            return

        try:
            f_old = Fernet(old_key)
            with open(path, "rb") as file:
                data = file.read()
            decrypted_temp = f_old.decrypt(data)

            new_key = Fernet.generate_key()
            self.root.ids.key_field.text = new_key.decode()

            f_new = Fernet(new_key)
            encrypted_new = f_new.encrypt(decrypted_temp)

            with open(path, "wb") as file:
                file.write(encrypted_new)

            toast(self.convert("تم تغيير المفتاح بنجاح"))
        except Exception as e:
            toast(self.convert("فشل العملية"))

    def show_info(self):
        toast("By: AboElfadl Media")

if __name__ == "__main__":
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    
    try:
        AboElfadlCipherApp().run()
    except Exception as e:
        print(e)