import requests
import telebot
import time
from telebot.apihelper import ApiException
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,Update
import os 

server=Flask(__name__)

TOKEN='توكن بوتك هنا'
bot=telebot.TeleBot(TOKEN)
gg='توكن بوتك'
@bot.message_handler(commands=['start'])
def check(message):
 id = message.from_user.id
 chat = "@malof_SD"
 conf = (f"https://api.telegram.org/bot{gg}/getChatMember?chat_id={chat}&user_id={id}")
 req1 = requests.get(conf)
 if ("left") in req1.text:
  bot.send_message(message.chat.id, f"يجب عليك الانضمام إلى القناة الخاصة بالبوت > {chat}")
 else:
  bot.send_message(message.chat.id, "مرحبًا بك")

TOKEN='توكن بوتك'
bot=telebot.TeleBot(TOKEN)

def start_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 2
    a=KeyboardButton('🔎 بحث عن عنوان IP')
    b=KeyboardButton('🔎 البحث عن النطاقات الفرعية')
    markup.row(a)
    markup.row(b)
    return markup

@bot.message_handler(commands=['start'])
def start_message(msg):
    bot.send_chat_action(msg.chat.id, 'typing')
    bot.send_message(msg.chat.id,'مرحبًا' + msg.from_user.first_name+"\nالاستخدام \n1. 🔎 * بحث عن عنوان IP * للعثور على تفاصيل العنوان IP\n\n2. 🔎 *البحث عن النطاقات الفرعية* للبحث عن النطاقات الفرعية لعنوان URL ",reply_markup=start_markup(),parse_mode='markdown')

   
@bot.message_handler(regexp='🔎 بحث عن عنوان IP')
def ip_handler(message):    
    bot.send_chat_action(message.chat.id, 'typing')
    sent = bot.send_message(message.chat.id, "أرسل عنوان IP")
    bot.register_next_step_handler(sent, ip)


def ip(message):
    ip=message.text
    url='http://ip-api.com/json/{}?fields=country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp'.format(ip)
    r=requests.get(url).json()
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id,'يعمل...')
    try: 
        country=r['country']
        countryCode=r['countryCode']
        region=r['region']
        regionName=r['regionName']
        city=r['city']
        zip_=r['zip']
        lat=r['lat']
        lon=r['lon']
        isp=r['isp']
        timezone=r['timezone']
        all_data=f'🚩*تفاصيل عنوان* {message.text}\n              𝙝𝙖𝙘𝙠𝙚𝙙 𝙗𝙮 𝙨𝙚𝙯𝙖𝙧 🦅\n🌐 *المنطقة :* {country}\n➖ *مرمز الدولة :* {countryCode}\n🏷 *المنطقة :* {region}\n🔺 *اسم المنطقة :* {regionName} \n✅ *المدينة :* {city}\n📍 *الرمز البريدي :* {zip_}\n📌 *خط العرض :* {lat}\n📌 *خط الطول :* {lon}\n⏰ *المنطقة الزمنية :* {timezone}\n⚙️ *مزود الخدمة :* {isp} . \nالقناة الخاصة بالبوت @malof_SD'
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id,all_data,parse_mode='markdown')
    except KeyError:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id,'❌ عنوان IP غير صالح')

@bot.message_handler(regexp='🔎 البحث عن النطاقات الفرعية')
def subdomains_handler(message):
        bot.send_chat_action(message.chat.id, 'typing')
        sent = bot.send_message(message.chat.id, "أدخل اسم المجال")
        bot.register_next_step_handler(sent, domain)

def domain(message):
    file=open('subdomains-1000.txt','r')
    content=file.read()
    subdomains=content.splitlines()
    total=[]
    urls=""
    bot.send_message(message.chat.id,"*جاري البحث عن النطاقات الفرعية ، قد يستغرق الأمر دقائق* ",parse_mode='markdown')
    for subdomain in subdomains:
        url="http://{}.{}".format(subdomain,message.text)
        try:
            requests.get(url)
        except requests.ConnectionError:
            pass
        else:
            total.append(url)
            urls+=url+"\n"
    data="✅ المجال : {}\n➖عدد النطاقات الفرعية : {}\n\n⚠️ النطاقات الفرعية المكتشفة:\n{}".format(message.text,len(total),urls)   
    bot.send_message(message.chat.id,data)


if __name__ == "__main__":
    bot.infinity_polling(True)