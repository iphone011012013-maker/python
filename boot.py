import logging
import random
import string
import datetime
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- إعدادات البوت ---
# استبدل هذا التوكن بالتوكن الخاص بك من BotFather
TOKEN = "7725928700:AAFN07OWx1xPNhvqRwaBskGz-9CvP6YV6W0"

# إعداد السجلات (Logging)
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
    await update.message.reply_text(
        "👋 أهلاً بك في بوت 'أبو الفضل' الخدمي الشامل!\n"
        "لدينا 49 خدمة متكاملة. اختر القسم المناسب:",
        reply_markup=reply_markup
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحكم في التنقل بين القوائم"""
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- قسم الإنتاجية ---
    if data == 'cat_productivity':
        keyboard = [
            [InlineKeyboardButton("1. تحويل لـ PDF", callback_data='srv_1'), InlineKeyboardButton("2. تفريغ صوتي", callback_data='srv_2')],
            [InlineKeyboardButton("3. تلخيص مقالات", callback_data='srv_3'), InlineKeyboardButton("4. OCR استخراج نص", callback_data='srv_4')],
            [InlineKeyboardButton("5. ضغط صور", callback_data='srv_5'), InlineKeyboardButton("6. إنشاء QR", callback_data='srv_6')],
            [InlineKeyboardButton("7. اختصار روابط", callback_data='srv_7'), InlineKeyboardButton("8. ترجمة فورية", callback_data='srv_8')],
            [InlineKeyboardButton("44. دمج PDF", callback_data='srv_44'), InlineKeyboardButton("49. PDF إلى نص", callback_data='srv_49')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]
        ]
        await query.edit_message_text("📂 **قسم الإنتاجية والملفات**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # --- قسم الأمن والشبكات ---
    elif data == 'cat_security':
        keyboard = [
            [InlineKeyboardButton("9. مراقبة الموقع", callback_data='srv_9'), InlineKeyboardButton("10. فحص الروابط", callback_data='srv_10')],
            [InlineKeyboardButton("11. Whois Info", callback_data='srv_11'), InlineKeyboardButton("12. كلمة مرور قوية", callback_data='srv_12')],
            [InlineKeyboardButton("13. فحص SSL", callback_data='srv_13'), InlineKeyboardButton("25. SSH Command", callback_data='srv_25')],
            [InlineKeyboardButton("30. موقع IP", callback_data='srv_30'), InlineKeyboardButton("31. فحص التسريب", callback_data='srv_31')],
            [InlineKeyboardButton("32. مسار الروابط", callback_data='srv_32'), InlineKeyboardButton("33. فحص المنافذ", callback_data='srv_33')],
            [InlineKeyboardButton("35. سجلات DNS", callback_data='srv_35'), InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]
        ]
        await query.edit_message_text("🛡️ **قسم الأمن السيبراني والشبكات**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # --- قسم التسويق ---
    elif data == 'cat_marketing':
        keyboard = [
            [InlineKeyboardButton("17. تحميل وسائط", callback_data='srv_17'), InlineKeyboardButton("18. هاشتاجات", callback_data='srv_18')],
            [InlineKeyboardButton("19. إزالة خلفية", callback_data='srv_19'), InlineKeyboardButton("20. جدولة نشر", callback_data='srv_20')],
            [InlineKeyboardButton("21. تحليل منافسين", callback_data='srv_21'), InlineKeyboardButton("22. صانع إعلانات", callback_data='srv_22')],
            [InlineKeyboardButton("41. علامة مائية", callback_data='srv_41'), InlineKeyboardButton("42. كثافة كلمات", callback_data='srv_42')],
            [InlineKeyboardButton("43. ميتا تاج", callback_data='srv_43'), InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]
        ]
        await query.edit_message_text("🚀 **قسم التسويق الإلكتروني**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # --- قسم المطورين ---
    elif data == 'cat_dev':
        keyboard = [
            [InlineKeyboardButton("14. استخراج ألوان", callback_data='srv_14'), InlineKeyboardButton("15. تحويل كود", callback_data='srv_15')],
            [InlineKeyboardButton("16. User Agent", callback_data='srv_16'), InlineKeyboardButton("26. SQL Query", callback_data='srv_26')],
            [InlineKeyboardButton("27. تنبيه القرص", callback_data='srv_27'), InlineKeyboardButton("36. تنسيق JSON", callback_data='srv_36')],
            [InlineKeyboardButton("37. بيانات وهمية", callback_data='srv_37'), InlineKeyboardButton("38. فحص Regex", callback_data='srv_38')],
            [InlineKeyboardButton("39. لقطة ويب", callback_data='srv_39'), InlineKeyboardButton("40. تحويل وحدات", callback_data='srv_40')],
            [InlineKeyboardButton("34. بيانات صور Exif", callback_data='srv_34'), InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]
        ]
        await query.edit_message_text("💻 **أدوات المطورين والبرمجة**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # --- قسم عام ومالي ---
    elif data == 'cat_general':
        keyboard = [
            [InlineKeyboardButton("23. الطقس", callback_data='srv_23'), InlineKeyboardButton("24. الصلاة", callback_data='srv_24')],
            [InlineKeyboardButton("28. بريد مؤقت", callback_data='srv_28'), InlineKeyboardButton("29. بحث صور", callback_data='srv_29')],
            [InlineKeyboardButton("45. فيديو لصوت", callback_data='srv_45'), InlineKeyboardButton("46. حساب خصم", callback_data='srv_46')],
            [InlineKeyboardButton("47. توقيت دولي", callback_data='srv_47'), InlineKeyboardButton("48. عقود", callback_data='srv_48')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='main_menu')]
        ]
        await query.edit_message_text("💰 **خدمات عامة ومالية**:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'main_menu':
        await start(update, context)

    else:
        # توجيه الطلب للدالة التي تنفذ الخدمة
        await execute_service(update, context, data)

# --- منطق الخدمات (Services Logic) ---

async def execute_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service_code):
    """تنفيذ المنطق الخاص بكل خدمة"""
    
    # ------------------ أدوات الأمن (تنفيذ حقيقي بسيط) ------------------
    if service_code == 'srv_12': # توليد كلمة مرور
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))
        await update.callback_query.message.reply_text(f"🔐 **كلمة المرور المقترحة:**\n`{password}`", parse_mode='Markdown')
        
    elif service_code == 'srv_16': # User Agent
        user_info = update.effective_user
        await update.callback_query.message.reply_text(f"👤 **معلوماتك:**\nID: `{user_info.id}`\nUsername: @{user_info.username}\nFull Name: {user_info.full_name}", parse_mode='Markdown')

    elif service_code == 'srv_10': # فحص روابط (محاكاة للتوعية)
        await update.callback_query.message.reply_text("⚠️ **وضع فحص الروابط:**\nأرسل الرابط الآن للتحقق منه (محاكاة لفحص Phishing).")
        context.user_data['waiting_for'] = 'link_scan'

    # ------------------ أدوات المطورين ------------------
    elif service_code == 'srv_36': # تنسيق JSON
        await update.callback_query.message.reply_text("أرسل كود JSON الفوضوي وسأقوم بترتيبه لك.")
        context.user_data['waiting_for'] = 'json_format'

    elif service_code == 'srv_37': # بيانات وهمية
        fake_data = f"Name: John Doe\nEmail: john{random.randint(100,999)}@example.com\nPhone: +1-555-01{random.randint(10,99)}"
        await update.callback_query.message.reply_text(f"🎭 **بيانات وهمية للتجربة:**\n{fake_data}")

    # ------------------ أدوات الإنتاجية ------------------
    elif service_code == 'srv_6': # QR Code (نظري)
        await update.callback_query.message.reply_text("أرسل النص أو الرابط لتحويله إلى QR Code.")
        context.user_data['waiting_for'] = 'qr_make'

    # ------------------ أدوات مالية ------------------
    elif service_code == 'srv_46': # حساب الخصم
        await update.callback_query.message.reply_text("أرسل السعر والخصم بهذا الشكل:\n1000 20\n(يعني السعر 1000 والخصم 20%)")
        context.user_data['waiting_for'] = 'calc_discount'

    # ------------------ باقي الخدمات (ردود جاهزة) ------------------
    else:
        # هنا تضع الأكواد الخاصة بباقي الـ 49 خدمة
        # نظراً لطول الكود، سأضع رسالة توضيحية للخدمات التي تحتاج APIs خارجية
        srv_name = service_code
        await update.callback_query.message.reply_text(f"🛠️ **الخدمة ({srv_name}) قيد الإنشاء.**\n\nلإكمال هذا البوت، تحتاج لربط هذه الخدمة بـ API خاص أو مكتبة Python (مثل OpenCV للصور أو Pandas للبيانات).")

# --- معالجة الرسائل النصية (Input Handlers) ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال النصوص من المستخدم ومعالجتها حسب الخدمة المختارة"""
    msg = update.message.text
    waiting_for = context.user_data.get('waiting_for')

    if waiting_for == 'link_scan':
        # منطق بسيط للتوعية
        if "http" not in msg:
            await update.message.reply_text("❌ هذا ليس رابطاً صالحاً.")
        elif "@" in msg or "-" in msg.split("//")[-1]: # كشف بدائي للتصيد
            await update.message.reply_text("⚠️ **تحذير:** هذا الرابط يبدو مشبوهاً (قد يحتوي على علامات تصيد).")
        else:
            await update.message.reply_text("✅ الرابط يبدو نظيفاً (بناءً على الفحص المبدئي).")
        context.user_data['waiting_for'] = None

    elif waiting_for == 'json_format':
        try:
            import json
            parsed = json.loads(msg)
            formatted = json.dumps(parsed, indent=4)
            await update.message.reply_text(f"📦 **JSON المنسق:**\n```json\n{formatted}\n```", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ كود JSON غير صحيح.")
        context.user_data['waiting_for'] = None

    elif waiting_for == 'calc_discount':
        try:
            parts = msg.split()
            price = float(parts[0])
            discount = float(parts[1])
            final = price - (price * (discount / 100))
            await update.message.reply_text(f"💰 **الحساب:**\nالسعر الأصلي: {price}\nقيمة الخصم: {discount}%\n السعر النهائي: {final}")
        except:
            await update.message.reply_text("❌ صيغة خاطئة. أرسل أرقام فقط.")
        context.user_data['waiting_for'] = None

    elif waiting_for == 'qr_make':
         # استخدام API خارجي لإنشاء QR لتجنب تنصيب مكتبات محلية
         qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={msg}"
         await update.message.reply_photo(qr_url, caption="✅ تم إنشاء الباركود.")
         context.user_data['waiting_for'] = None

    else:
        await update.message.reply_text("يرجى اختيار خدمة من القائمة أولاً /start")

# --- التشغيل الرئيسي ---

def main():
    """تشغيل البوت"""
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern='^cat_')) # للقوائم الرئيسية
    application.add_handler(CallbackQueryHandler(menu_handler, pattern='^srv_')) # للأزرار الفرعية (العودة)
    application.add_handler(CallbackQueryHandler(menu_handler, pattern='^main_menu'))
    
    # التقاط ضغطات الخدمات وتنفيذها
    # ملاحظة: في الكود أعلاه دمجنا التنقل والتنفيذ في دالة واحدة لتبسيط الكود، 
    # لكن يمكن فصل `srv_` لمعالج خاص. هنا سيذهب لـ menu_handler ويوجه لـ execute_service
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()