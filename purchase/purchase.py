import configparser
import telebot


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
token = config['Telegram']['token'] # обращаемся как к обычному словарю!

bot=telebot.TeleBot(token)

@bot.message_handler(commands=['hello'])
def hello_message(message):
	bot.send_message(message.chat.id,"Привет ✌️ ")
	bot.reply_to(message=message, text=str(message.chat.id))
bot.infinity_polling()
