import os, logging, asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

# استيراد الخدمات والدوال الجديدة
from services import (
    HANDLERS_MAP, 
    hdl_ocr_image, 
    do_ocr, 
    WAIT_OCR_PHOTO
)

# ---------- إعدادات أساسية ----------
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- أوامر القائمة ----------
COMMANDS = [
    BotCommand("start", "القائمة الرئيسية"),
    BotCommand("cancel", "إلغاء العملية الحالية"),
]

# ... (نفس كود SERVICES والقائمة والأزرار لم يتغير) ...
SERVICES = [
    ["تحويل ملفات (صورة↔PDF، Word↔PDF)", "file_convert"],
    ["تفريغ صوتي (Voice Notes→نص)", "audio_transcribe"],
    ["تلخيص مقال من رابط", "summarize_url"],
    ["استخراج نصوص من صور (OCR)", "ocr_image"], # هذا الزر سيستدعي الـ ConversationHandler
    ["ضغط الصور", "compress_img"],
    ["إنشاء QR Code", "qr_gen"],
    ["اختصار الروابط", "shorten_link"],
    ["ترجمة فورية للمجموعات", "group_translate"],
    ["مراقبة uptime موقع", "uptime_monitor"],
    ["فحص روابط (فيروسات/تصيد)", "link_scan"],
    # ... بقية الخدمات ...
]
# ... (دوال build_menu و split_pages كما هي) ...

PAGE_SIZE = 10
TOTAL_PAGES = (len(SERVICES) + PAGE_SIZE - 1) // PAGE_SIZE

def split_pages() -> list:
    pages = []
    for p in range(TOTAL_PAGES):
        start, end = p * PAGE_SIZE, (p + 1) * PAGE_SIZE
        pages.append(SERVICES[start:end])
    return pages

def build_menu(page: int = 0) -> InlineKeyboardMarkup:
    pages = split_pages()
    buttons = []
    for desc, cb in pages[page]:
        buttons.append([InlineKeyboardButton(desc, callback_data=cb)])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{TOTAL_PAGES}", callback_data="noop"))
    if page < TOTAL_PAGES - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))
    buttons.append(nav)
    buttons.append([InlineKeyboardButton("❌ إغلاق", callback_data="close")])
    return InlineKeyboardMarkup(buttons)

# ---------- أوامر بدائية ----------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **أهلاً بك في بوت الخدمات الشامل**\nاختر خدمة من القائمة:",
        reply_markup=build_menu(),
        parse_mode="Markdown"
    )

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ تم إلغاء العملية والعودة للوضع الطبيعي.")
    return ConversationHandler.END

async def close_panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.delete()

async def navigate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await q.edit_message_reply_markup(reply_markup=build_menu(page))
    elif data == "close":
        await q.message.delete()
    elif data == "noop":
        await q.answer(" ")

# ---------- توزيع الخدمات العادية ----------
async def route_service(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    # لا نقوم بعمل answer هنا لأن الـ handler قد يكون غير موجود ويسبب تعليق
    service = q.data
    handler = HANDLERS_MAP.get(service)
    if handler:
        await q.answer()
        await handler(update, ctx)
    else:
        await q.answer("⚠️ هذه الخدمة قيد التطوير...", show_alert=True)

# ---------- تشغيل البوت ----------
def main():
    app = Application.builder().token(TOKEN).post_init(lambda app: app.bot.set_my_commands(COMMANDS)).build()

    # 1. إعداد ConversationHandler لخدمة OCR
    ocr_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(hdl_ocr_image, pattern="^ocr_image$")],
        states={
            WAIT_OCR_PHOTO: [MessageHandler(filters.PHOTO, do_ocr)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False # مهم لضمان استمرار الحالة مع المستخدم
    )

    # 2. إضافة الـ Handlers بالترتيب الصحيح (الأولوية للخاص ثم العام)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # إضافة OCR Handler قبل الـ Generic Handler
    app.add_handler(ocr_conv)
    
    # التنقل بين الصفحات
    app.add_handler(CallbackQueryHandler(navigate, pattern="^(page_|close|noop)"))
    
    # بقية الخدمات (Generic Routing)
    app.add_handler(CallbackQueryHandler(route_service, pattern="^((?!page_|close|noop|ocr_image).)*$"))

    logger.info("Bot started successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()