import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- 1. دوال التشفير ---
def get_key_from_password(password, salt=b'MyFixedSalt123'):
    """توليد مفتاح من كلمة السر"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_specific_file(file_path, password):
    """دالة التشفير"""
    try:
        # التأكد من وجود الملف أولاً
        if not os.path.exists(file_path):
            print(f"⚠️ الملف غير موجود: {file_path}")
            return

        print("⏳ جاري التشفير...")
        key = get_key_from_password(password)
        fernet = Fernet(key)

        with open(file_path, "rb") as file:
            original_data = file.read()

        encrypted_data = fernet.encrypt(original_data)

        with open(file_path + ".enc", "wb") as file:
            file.write(encrypted_data)
            
        print(f"✅ تم بنجاح تشفير الملف: {file_path}")
        print(f"📄 الملف الجديد اسمه: {file_path}.enc")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

# --- 2. طريقة الاستخدام ---

# قم بإنشاء ملف تجريبي اسمه test_file.txt بجانب الكود لتجربته
target_file = "test_file.txt" 
my_pass = "mahmoud"

print(f"--- نظام تشفير أبو الفضل ---")
print(f"جاري البحث عن ملف: {target_file}")

# استدعاء الدالة
encrypt_specific_file(target_file, my_pass)

# --- 3. الحل لمشكلة الإغلاق ---
print("\n--------------------------------")
input("اضغط على زر Enter للخروج من البرنامج...")