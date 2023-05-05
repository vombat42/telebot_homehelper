import configparser
import telebot


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
token = config['Telegram']['token'] # обращаемся как к обычному словарю!
print(token)

bot=telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Привет ✌️ ")

bot.infinity_poling()
