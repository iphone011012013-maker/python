from telebot import TeleBot
import telebot
webbrowser.open('https://t.me/bsx_h2')
bot = telebot.TeleBot('6176067227:AAGwBfz1BGAAt0PMk9B2-hcXGfuAzNPcks8')

@bot.message_handler(commands=['start'])
def home(message):
    bot.send_message(chat_id=message.chat.id, text='Send IP.')
@bot.message_handler(func=lambda call:True)
def working(message):
    ip = message.text
    location = lookup(ip_addr=ip)
    if location is None:
        bot.send_message(chat_id=message.chat.id, text='IP None')
    else:
        with open(ip + '8.txt', 'a') as hrr:
            hrr.write(str(location.location) + '\n')
        file2 = open(ip + '8.txt', 'r').read()
        lad = file2.split('(')[1].split(',')[0]
        log = file2.split('(')[1].split(')')[0].split(', ')[1]
        bot.send_location(chat_id=message.chat.id, latitude=lad, longitude=log)
bot.infinity_polling()