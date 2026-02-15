import telebot
from telebot import types
import requests , re

token = "8074252682:AAEVcKbV4oAz4nY44Pin6TnpsRuV8N74nds"
channel = types.InlineKeyboardButton(text='my channel',url='t.me/hexada_tech')
bot = telebot.TeleBot(token)
#تذكر مصدري قناتي @hexada_tech
#برمجة 
@bot.message_handler(commands=["start"])
def welcome(message):
	name = message.from_user.first_name
	brok = types.InlineKeyboardMarkup()
	brok.add(channel)
	bot.reply_to(message,'welcome hey {} send Your Url to Shorten. ♾'.format(name),reply_markup=brok)
	
@bot.message_handler(func=lambda m:True)
def shorturl(message):
	msg = message.text
	url = f'https://is.gd/create.php?format=simple&url={msg}'
	req = requests.get(url).text
	if re.search("(?P<url>https?://[^\s]+)", msg):
		bot.reply_to(message,f'New Url :\n{req}')
	else:
		bot.reply_to(message, "sorry ,This is not a link URL")
	
print('run')
bot.infinity_polling()