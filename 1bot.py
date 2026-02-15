import logging
import random
import string
import os
import requests
from pypdf import PdfWriter
from deep_translator import GoogleTranslator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- إعدادات البوت ---
# تم وضع التوكن الخاص بك هنا
TOKEN = "7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0"

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- القوائم (Menus) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرسالة الترحيبية والقائمة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("📂 الإنتاجية والملفات", callback_data='cat_productivity')],
        [InlineKeyboardButton("🛡️ الأمن والشبكات", callback_data='cat_security')],
        [InlineKeyboardButton("🚀 التسويق والنمو", callback_data='cat_marketing')],
        [InlineKeyboardButton("💻 أدوات المطورين", callback_data='cat_dev')],
        [InlineKeyboardButton("💰 خدمات مالية وعامة", callback_data='cat_general')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_msg = (
        "👋 أهلاً بك في بوت 'أبو الفضل' (AboElfadl Tech)!\n"
        "أنا المساعد الرقمي الشامل. اختر القسم للبدء:"
    )
    if update.message:
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_msg, reply_markup=reply_markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحكم في التنقل بين القوائم"""
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- القوائم الفرعية ---
    if data == 'cat_productivity':
        keyboard = [
            [InlineKeyboardButton("4. OCR استخراج نص 📷", callback_data='srv_4')],
            [InlineKeyboardButton("8. ترجمة فورية 🌐", callback_data='srv_8')],
            [InlineKeyboardButton("44. دمج PDF 📑", callback_data='srv_44')],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
        ]
        await query.edit_message_text("📂 **قسم الإنتاجية والملفات**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'cat_security':
        keyboard = [
            [InlineKeyboardButton("12. كلمة مرور قوية 🔐", callback_data='srv_12')],
            [InlineKeyboardButton("10. فحص روابط 🛡️", callback_data='srv_10')],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
        ]
        await query.edit_message_text("🛡️ **قسم الأمن السيبراني**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'cat_marketing':
        keyboard = [
            [InlineKeyboardButton("22. صانع إعلانات (بسيط)", callback_data='srv_22')],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
        ]
        await query.edit_message_text("🚀 **قسم التسويق الإلكتروني**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'cat_dev':
        keyboard = [
            [InlineKeyboardButton("36. تنسيق JSON", callback_data='srv_36')],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
        ]
        await query.edit_message_text("💻 **أدوات المطورين والبرمجة**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'cat_general':
        keyboard = [
            [InlineKeyboardButton("46. حساب الخصم", callback_data='srv_46')],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
        ]
        await query.edit_message_text("💰 **خدمات عامة ومالية**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == 'main_menu':
        await start(update, context)

    elif data.startswith('srv_'):
        await execute_service(update, context, data)
    
    else:
        await start(update, context)

# --- منطق الخدمات (Services Logic) ---

async def execute_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service_code):
    """تنفيذ المنطق والتهيئة للخدمة"""
    
    # 1. خدمة الترجمة الفورية (srv_8)
    if service_code == 'srv_8':
        await update.callback_query.message.reply_text("🌐 **خدمة الترجمة الفورية**\nأرسل أي نص الآن (بأي لغة) وسأقوم بترجمته للعربية فوراً.")
        context.user_data['waiting_for'] = 'translate_text'

    # 2. خدمة استخراج النص OCR (srv_4)
    elif service_code == 'srv_4':
        await update.callback_query.message.reply_text("📷 **خدمة استخراج النص (OCR)**\nأرسل صورة (واضحة) تحتوي على نص إنجليزي أو عربي، وسأقوم باستخراجه لك.")
        context.user_data['waiting_for'] = 'ocr_photo'

    # 3. خدمة دمج ملفات PDF (srv_44)
    elif service_code == 'srv_44':
        context.user_data['pdf_list'] = [] # تهيئة القائمة
        context.user_data['waiting_for'] = 'merge_pdf'
        keyboard = [[InlineKeyboardButton("✅ تم الإرسال (دمج الآن)", callback_data='do_merge_pdf')]]
        await update.callback_query.message.reply_text(
            "📑 **خدمة دمج ملفات PDF**\n"
            "1. أرسل ملفات PDF واحداً تلو الآخر.\n"
            "2. عند الانتهاء، اضغط على الزر أدناه.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 4. زر تنفيذ الدمج (تابع لـ srv_44)
    elif service_code == 'do_merge_pdf':
        pdf_files = context.user_data.get('pdf_list', [])
        if not pdf_files:
            await update.callback_query.message.reply_text("❌ لم ترسل أي ملفات لدمجها!")
            return
        
        await update.callback_query.message.reply_text("⚙️ جاري دمج الملفات... انتظر لحظة.")
        
        try:
            merger = PdfWriter()
            for pdf in pdf_files:
                merger.append(pdf)
            
            output_filename = f"merged_{random.randint(1000,9999)}.pdf"
            merger.write(output_filename)
            merger.close()
            
            # إرسال الملف الناتج
            await update.callback_query.message.reply_document(
                document=open(output_filename, 'rb'),
                caption="✅ تم دمج الملفات بنجاح! | AboElfadl Tools"
            )
            
            # تنظيف الملفات
            os.remove(output_filename)
            for pdf in pdf_files:
                try: os.remove(pdf)
                except: pass
            context.user_data['pdf_list'] = []
            
        except Exception as e:
            await update.callback_query.message.reply_text(f"حدث خطأ أثناء الدمج: {str(e)}")
        
        context.user_data['waiting_for'] = None

    # خدمات أمنية (srv_12)
    elif service_code == 'srv_12':
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))
        await update.callback_query.message.reply_text(f"🔐 **كلمة مرور قوية:** `{password}`", parse_mode='Markdown')
    
    # خدمات الروابط (srv_10)
    elif service_code == 'srv_10':
         await update.callback_query.message.reply_text("🛡️ أرسل الرابط لفحصه الآن (فحص أولي).")
         context.user_data['waiting_for'] = 'link_scan'
    
    # خدمات المطورين (srv_36)
    elif service_code == 'srv_36':
        await update.callback_query.message.reply_text("أرسل كود JSON الفوضوي وسأقوم بترتيبه لك.")
        context.user_data['waiting_for'] = 'json_format'

    # خدمات مالية (srv_46)
    elif service_code == 'srv_46': 
        await update.callback_query.message.reply_text("أرسل السعر والخصم بهذا الشكل:\n1000 20\n(يعني السعر 1000 والخصم 20%)")
        context.user_data['waiting_for'] = 'calc_discount'

    else:
        await update.callback_query.message.reply_text("⚠️ هذه الخدمة قيد التطوير في التحديث القادم.")

# --- معالجة المدخلات (نصوص، صور، ملفات) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    waiting_for = context.user_data.get('waiting_for')

    # -- معالجة الترجمة --
    if waiting_for == 'translate_text':
        try:
            translated = GoogleTranslator(source='auto', target='ar').translate(msg)
            await update.message.reply_text(f"🔤 **الترجمة:**\n{translated}")
        except Exception as e:
            await update.message.reply_text("عذراً، حدث خطأ في خدمة الترجمة.")

    # -- معالجة فحص الروابط --
    elif waiting_for == 'link_scan':
        if "http" not in msg:
             await update.message.reply_text("❌ رابط غير صالح.")
        elif "@" in msg or "-" in msg.split("//")[-1] if "//" in msg else False: 
             await update.message.reply_text("⚠️ **تحذير:** هذا الرابط يبدو مشبوهاً (قد يحتوي على علامات تصيد).")
        else:
             await update.message.reply_text("✅ (فحص أولي) الرابط يبدو سليماً هيكلياً، لكن توخ الحذر.")
        context.user_data['waiting_for'] = None

    # -- معالجة JSON --
    elif waiting_for == 'json_format':
        try:
            import json
            parsed = json.loads(msg)
            formatted = json.dumps(parsed, indent=4)
            await update.message.reply_text(f"📦 **JSON المنسق:**\n```json\n{formatted}\n```", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ كود JSON غير صحيح.")
        context.user_data['waiting_for'] = None

    # -- معالجة الخصم --
    elif waiting_for == 'calc_discount':
        try:
            parts = msg.split()
            price = float(parts[0])
            discount = float(parts[1])
            final = price - (price * (discount / 100))
            await update.message.reply_text(f"💰 **الحساب:**\nالسعر الأصلي: {price}\nقيمة الخصم: {discount}%\n السعر النهائي: {final}")
        except:
            await update.message.reply_text("❌ صيغة خاطئة. أرسل أرقام فقط (مثال: 500 10).")
        context.user_data['waiting_for'] = None

    else:
        await update.message.reply_text("يرجى اختيار خدمة من القائمة /start")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الصور (للـ OCR)"""
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'ocr_photo':
        status_msg = await update.message.reply_text("⏳ جاري تحليل الصورة واستخراج النص...")
        try:
            photo_file = await update.message.photo[-1].get_file()
            file_path = f"temp_ocr_{random.randint(100,999)}.jpg"
            await photo_file.download_to_drive(file_path)
            
            # استخدام API مجاني لـ OCR (OCR.space)
            api_url = 'https://api.ocr.space/parse/image'
            with open(file_path, 'rb') as f:
                payload = {
                    'apikey': 'helloworld',
                    'language': 'ara', 
                    'isOverlayRequired': False
                }
                files = {'file': f}
                response = requests.post(api_url, files=files, data=payload)
            
            result = response.json()
            parsed_text = result.get('ParsedResults')[0].get('ParsedText')
            
            if parsed_text:
                await status_msg.edit_text(f"📝 **النص المستخرج:**\n\n{parsed_text}")
            else:
                await status_msg.edit_text("❌ لم أتمكن من العثور على نص واضح.")
            
            os.remove(file_path)
            
        except Exception as e:
            await status_msg.edit_text(f"حدث خطأ: {e}")
        
        context.user_data['waiting_for'] = None

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الملفات (لدمج PDF)"""
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'merge_pdf':
        doc = update.message.document
        if doc.mime_type and 'pdf' in doc.mime_type:
            file_id = doc.file_id
            new_file = await context.bot.get_file(file_id)
            file_name = f"temp_{doc.file_name}"
            await new_file.download_to_drive(file_name)
            
            if 'pdf_list' not in context.user_data:
                context.user_data['pdf_list'] = []
            context.user_data['pdf_list'].append(file_name)
            
            count = len(context.user_data['pdf_list'])
            keyboard = [[InlineKeyboardButton("✅ تم الإرسال (دمج الآن)", callback_data='do_merge_pdf')]]
            await update.message.reply_text(f"📥 تم استلام الملف رقم {count}. أرسل التالي أو اضغط دمج.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ يرجى إرسال ملفات بصيغة PDF فقط.")

# --- التشغيل الرئيسي ---

def main():
    """تشغيل البوت"""
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern='^cat_')) 
    application.add_handler(CallbackQueryHandler(menu_handler, pattern='^srv_')) 
    application.add_handler(CallbackQueryHandler(menu_handler, pattern='^main_menu'))
    application.add_handler(CallbackQueryHandler(execute_service, pattern='^do_merge_pdf')) 

    # Message Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo)) 
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document)) 

    print("🤖 بوت أبو الفضل (AboElfadl Tech) يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()
```

### 🏁 خطوات التشغيل النهائية (Final Checklist):
1.  تأكد أنك قمت بتثبيت المكتبات المطلوبة في الـ Terminal:
    ```bash
    pip install python-telegram-bot deep-translator pypdf requests