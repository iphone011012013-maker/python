import os
import tempfile
import asyncio
import logging
import pytesseract
from PIL import Image as PILImage
import aiofiles
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import qrcode
import random
import string
import requests
import whois
from faker import Faker
import pyshorteners
from io import BytesIO

# ==========================================
# ⚙️ إعدادات النظام
# ==========================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
WAIT_OCR_PHOTO = 1
WAIT_INPUT_DATA = 2  # حالة انتظار عامة للمدخلات

# ==========================================
# 🛠️ أدوات مساعدة
# ==========================================
async def download_file(file_obj, ext: str) -> Path:
    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    tmp_path = Path(path)
    async with aiofiles.open(tmp_path, "wb") as f:
        await f.write(await file_obj.download_as_bytearray())
    return tmp_path

# ==========================================
# 1. خدمة OCR (تم تفعيلها سابقاً)
# ==========================================
async def hdl_ocr_image(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📸 أرسل الصورة لاستخراج النص منها (عربي/إنجليزي).")
    return WAIT_OCR_PHOTO

async def do_ocr(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ جاري المعالجة...")
    tmp_path = None
    try:
        photo = update.message.photo[-1]
        file_obj = await photo.get_file()
        tmp_path = await download_file(file_obj, ".jpg")
        
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(PILImage.open(tmp_path), lang='ara+eng', config=custom_config)
        
        if len(text.strip()) > 0:
            if len(text) > 4000:
                # إرسال كملف نصي إذا كان طويلاً
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(text)
                    f_path = f.name
                await update.message.reply_document(open(f_path, 'rb'), caption="📄 النص طويل جداً، تم وضعه في ملف.")
                os.remove(f_path)
            else:
                await msg.edit_text(f"📝 النص المستخرج:\n\n`{text}`", parse_mode="Markdown")
        else:
            await msg.edit_text("⚠️ لم يتم العثور على نص واضح.")
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {e}")
    finally:
        if tmp_path: tmp_path.unlink(missing_ok=True)
    return ConversationHandler.END

# ==========================================
# 2. خدمة ضغط الصور (Compress Image)
# ==========================================
async def hdl_compress_img(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🖼️ أرسل الصورة التي تريد ضغط حجمها.")
    ctx.user_data['service_mode'] = 'compress'
    return WAIT_INPUT_DATA

async def do_compress(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ جاري الضغط...")
    try:
        photo = update.message.photo[-1]
        file_obj = await photo.get_file()
        tmp_path = await download_file(file_obj, ".jpg")
        
        # ضغط الصورة باستخدام Pillow
        img = PILImage.open(tmp_path)
        output = BytesIO()
        img.save(output, format="JPEG", quality=40, optimize=True)
        output.seek(0)
        
        await update.message.reply_photo(photo=output, caption="✅ تم ضغط الصورة.")
        tmp_path.unlink()
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {e}")
    return ConversationHandler.END

# ==========================================
# 3. خدمة QR Code
# ==========================================
async def hdl_qr_gen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📩 أرسل النص أو الرابط لتحويله لـ QR Code.")
    ctx.user_data['service_mode'] = 'qrcode'
    return WAIT_INPUT_DATA

async def do_qr_gen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        await update.message.reply_text("الرجاء إرسال نص فقط.")
        return ConversationHandler.END
    
    img = qrcode.make(text)
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption="✅ تم إنشاء الباركود.")
    return ConversationHandler.END

# ==========================================
# 4. خدمة توليد كلمات مرور (Gen Pass)
# ==========================================
async def hdl_gen_pass(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # هذه الخدمة لا تحتاج انتظار مدخلات، تنفذ فوراً
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = "".join(random.choice(chars) for _ in range(16))
    await update.callback_query.message.reply_text(f"🔐 كلمة مرور قوية مقترحة:\n\n`{password}`", parse_mode="Markdown")

# ==========================================
# 5. خدمة اختصار الروابط (Shorten Link)
# ==========================================
async def hdl_shorten_link(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🔗 أرسل الرابط الطويل لاختصاره.")
    ctx.user_data['service_mode'] = 'shorten'
    return WAIT_INPUT_DATA

async def do_shorten(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'):
        await update.message.reply_text("⚠️ الرابط يجب أن يبدأ بـ http أو https")
        return ConversationHandler.END
    
    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(url)
        await update.message.reply_text(f"✅ الرابط المختصر:\n{short_url}")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")
    return ConversationHandler.END

# ==========================================
# 6. خدمة Whois (معلومات النطاق)
# ==========================================
async def hdl_whois_domain(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🌐 أرسل اسم النطاق (مثال: google.com).")
    ctx.user_data['service_mode'] = 'whois'
    return WAIT_INPUT_DATA

async def do_whois(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.replace("https://", "").replace("http://", "").split('/')[0]
    msg = await update.message.reply_text("🔎 جاري البحث...")
    try:
        w = whois.whois(domain)
        info = f"📅 تاريخ الإنشاء: {w.creation_date}\n"
        info += f"🛑 تاريخ الانتهاء: {w.expiration_date}\n"
        info += f"🏢 المسجل: {w.registrar}"
        await msg.edit_text(f"🌐 معلومات {domain}:\n\n{info}")
    except:
        await msg.edit_text("❌ لم يتم العثور على معلومات لهذا النطاق.")
    return ConversationHandler.END

# ==========================================
# 7. خدمة IP Geolocation
# ==========================================
async def hdl_ip_geo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📍 أرسل رقم الـ IP لمعرفة موقعه.")
    ctx.user_data['service_mode'] = 'ip_geo'
    return WAIT_INPUT_DATA

async def do_ip_geo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ip = update.message.text.strip()
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        if r['status'] == 'success':
            txt = f"🌍 الدولة: {r['country']}\n🏙 المدينة: {r['city']}\n📡 المزود: {r['isp']}"
            await update.message.reply_text(txt)
        else:
            await update.message.reply_text("❌ IP غير صحيح.")
    except:
        await update.message.reply_text("❌ خطأ في الاتصال.")
    return ConversationHandler.END

# ==========================================
# 8. خدمة البيانات الوهمية (Fake Data)
# ==========================================
async def hdl_fake_data(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    fake = Faker()
    data = f"👤 الاسم: {fake.name()}\n🏠 العنوان: {fake.address()}\n📧 الايميل: {fake.email()}\n💼 الوظيفة: {fake.job()}"
    await update.callback_query.message.reply_text(f"🎭 بيانات وهمية:\n\n{data}")

# ==========================================
# معالج المدخلات العام (General Input Handler)
# ==========================================
# هذه الدالة توزع المدخلات بناءً على الزر الذي ضغطه المستخدم
async def handle_user_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    mode = ctx.user_data.get('service_mode')
    
    if mode == 'compress':
        return await do_compress(update, ctx)
    elif mode == 'qrcode':
        return await do_qr_gen(update, ctx)
    elif mode == 'shorten':
        return await do_shorten(update, ctx)
    elif mode == 'whois':
        return await do_whois(update, ctx)
    elif mode == 'ip_geo':
        return await do_ip_geo(update, ctx)
    else:
        await update.message.reply_text("⚠️ الرجاء اختيار خدمة من القائمة أولاً.")
        return ConversationHandler.END

# ==========================================
# بقية الخدمات (Placeholders للمرحلة القادمة)
# ==========================================
async def dummy_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("🔜 هذه الخدمة قادمة في التحديث القادم!", show_alert=True)

# خريطة التوجيه
HANDLERS_MAP = {
    # تم التفعيل
    "ocr_image": hdl_ocr_image,
    "compress_img": hdl_compress_img,
    "qr_gen": hdl_qr_gen,
    "gen_pass": hdl_gen_pass,
    "shorten_link": hdl_shorten_link,
    "whois_domain": hdl_whois_domain,
    "ip_geo": hdl_ip_geo,
    "fake_data": hdl_fake_data,
    
    # قيد الانتظار (سيتم استخدام dummy_handler مؤقتاً)
    "file_convert": dummy_handler,
    "audio_transcribe": dummy_handler,
    # ... يمكنك إضافة الباقي هنا وتوجيهه لـ dummy_handler
}