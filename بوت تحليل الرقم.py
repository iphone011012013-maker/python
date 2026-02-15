import telebot
import phonenumbers
from phonenumbers import geocoder, carrier, timezone, phonenumberutil

# التوكن الخاص بك
TOKEN = '8074252682:AAEVcKbV4oAz4nY44Pin6TnpsRuV8N74nds'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_msg = (
        "🛡️ **نظام AboElfadl لتحليل الأرقام المتكامل**\n\n"
        "أرسل رقم الهاتف كاملاً مع مفتاح الدولة (مثال: `+2010...`)\n"
        "سيقوم النظام باستخراج كافة البيانات المتاحة عالمياً."
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def track_number(message):
    try:
        num = message.text
        # التحليل الأساسي
        parsed_num = phonenumbers.parse(num, None)
        
        # 1. التحقق من صحة الرقم
        is_valid = phonenumbers.is_valid_number(parsed_num)
        # 2. استخراج نوع الخط (موبايل، أرضي، إلخ)
        number_type = phonenumberutil.number_type(parsed_num)
        type_str = "غير معروف"
        if number_type == phonenumberutil.PhoneNumberType.MOBILE: type_str = "جوال (Mobile)"
        elif number_type == phonenumberutil.PhoneNumberType.FIXED_LINE: type_str = "خط أرضي (Fixed Line)"
        
        # 3. استخراج الدولة والشركة
        country = geocoder.description_for_number(parsed_num, "ar")
        service_provider = carrier.name_for_number(parsed_num, "ar")
        
        # 4. استخراج المنطقة الزمنية
        time_zones = timezone.time_zones_for_number(parsed_num)
        
        # 5. التنسيق الدولي والوطني
        intl_format = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        local_format = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.NATIONAL)

        # واجهة المستخدم الاحترافية (UI) كما تحب في مشاريعك
        response = (
            f"🔎 **تقرير تحليل الرقم: {intl_format}**\n"
            f"━━━━━━━━━━━━━━\n"
            f"✅ **حالة الرقم:** {'صالح (Valid)' if is_valid else 'غير صالح'}\n"
            f"🌍 **الدولة:** {country}\n"
            f"🏢 **المشغل (Carrier):** {service_provider if service_provider else 'غير متوفر'}\n"
            f"📱 **نوع الخط:** {type_str}\n"
            f"📍 **التنسيق المحلي:** `{local_format}`\n"
            f"⏰ **التوقيت الزمني:** {', '.join(time_zones)}\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 *تم التحليل بواسطة نظام AboElfadl للتوعية*"
        )
        bot.reply_to(message, response, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, "❌ **خطأ:** تعذر تحليل هذا الرقم. تأكد من إضافة علامة (+) ومفتاح الدولة.")

print("البوت الاحترافي يعمل الآن...")
bot.polling()