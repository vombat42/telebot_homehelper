import configparser
import telebot
from telebot import types


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
token = config['Telegram']['token'] # обращаемся как к обычному словарю!

bot=telebot.TeleBot(token)

def privet(message):
	return message.text == 'Привет'

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Приступим :)")

@bot.message_handler(commands=['hello'])
def hello_message(message):
	# bot.reply_to(message=message, text=str(message.chat.id))
	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	item1 = types.KeyboardButton('Отжимания')
	item2 = types.KeyboardButton('Приседания')
	item3 = types.KeyboardButton('Икры')
	item4 = types.KeyboardButton('Пресс')
	markup.add(item1, item2, item3, item4)
	bot.send_message(message.chat.id,"Привет, {0.first_name}! ✌️ ".format(message.from_user), reply_markup = markup)



@bot.message_handler(commands=['report'])
def report_message(message):
	bot.send_message(message.chat.id,"Вот твой отчет")

@bot.message_handler(func = privet)
def message_message(message):
	bot.send_message(message.chat.id,"И вам не хворать")

bot.infinity_polling()
