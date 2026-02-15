import telebot
from telebot import types
import base64

token = "token"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    btn1 = types.InlineKeyboardButton('تشفير ملف', callback_data='en')
    btn2 = types.InlineKeyboardButton('فك تشفير ملف', callback_data='de')
    xx = types.InlineKeyboardMarkup()
    xx.add(btn1)
    xx.add(btn2)
    bot.reply_to(message, f'مرحبا بك عزيزي المستخدم [{name}](tg://settings)\n\n- في بوت تشفير وفك تشفير Base64\n\n- للبدأ اضغط علي بدأ الاستخدام\n @llxxx3 ',
                 reply_markup=xx, parse_mode="markdown")


@bot.callback_query_handler(func=lambda call: True)
def code(call):
    if call.data == 'en':
        bot.send_message(call.message.chat.id, '*أرسل الملف الآن لتشفيره لك*', parse_mode="markdown")
        bot.register_next_step_handler(call.message, en_file)
    elif call.data == 'de':
        bot.send_message(call.message.chat.id, '*أرسل الملف الآن لفك تشفيره*', parse_mode="markdown")
        bot.register_next_step_handler(call.message, de_file)


def en_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        encoded_file = base64.b64encode(downloaded_file)
        bot.send_document(message.chat.id, encoded_file)
        bot.reply_to(message, '*تم تشفير الملف بنجاح* \n@llxxx3', parse_mode="markdown")
    else:
        bot.reply_to(message, 'يجب إرسال ملف لتشفيره.')


def de_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        decoded_file = base64.b64decode(downloaded_file)
        bot.send_document(message.chat.id, decoded_file)
        bot.reply_to(message, '*تم فك تشفير الملف بنجاح* \n@llxxx3', parse_mode="markdown")
    else:
        bot.reply_to(message, 'يجب إرسال ملف لفك تشفيره.')


bot.polling()