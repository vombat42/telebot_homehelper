import configparser
import telebot
from telebot import types

#----------------------------------------------------------------------------


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
token = config['Telegram']['token'] # обращаемся как к обычному словарю!

bot=telebot.TeleBot(token)

# формируем клавиатуру с упражнениями
buttons=('Отжимания','Икры','Пресс','Приседания','Планка','Наклоны','Спина','Шея')
markup_ex = types.InlineKeyboardMarkup(row_width=3)
item =[]
for i in range(0,len(buttons), 3):
	if len(buttons)-i>=3:
		item1=types.InlineKeyboardButton(text=buttons[i], callback_data=buttons[i])
		item2=types.InlineKeyboardButton(text=buttons[i+1], callback_data=buttons[i+1])
		item3=types.InlineKeyboardButton(text=buttons[i+2], callback_data=buttons[i+2])
	elif len(buttons)-i==2:
		item1=types.InlineKeyboardButton(text=buttons[i], callback_data=buttons[i])
		item2=types.InlineKeyboardButton(text=buttons[i+1], callback_data=buttons[i+1])
		item3=types.InlineKeyboardButton(text=' ', callback_data=' ')
	elif len(buttons)-i==1:
		item1=types.InlineKeyboardButton(text=buttons[i], callback_data=buttons[i])
		item2=types.InlineKeyboardButton(text=' ', callback_data=' ')
		item3=types.InlineKeyboardButton(text=' ', callback_data=' ')
	markup_ex.add(item1, item2, item3)


#----------------------------------------------------------------------------

# кто не в списке userlist - проходит мимо
userlist=(406827859,)
@bot.message_handler(func=lambda message: message.chat.id not in userlist)
def some(message):
   bot.send_message(message.chat.id, "Sorry")

#----------------------------------------------------------------------------



@bot.callback_query_handler(func=lambda call: True)
def check_callback(call):
	if call.data == 'Отжимания':
		bot.send_message(call.message.chat.id, '-Отжимания-')
		# bot.answer_callback_query(callback.id, "Answer is Yes")
	elif call.data == 'Икры':
		bot.send_message(call.message.chat.id, '-Икры-')
	bot.answer_callback_query(call.id, "Answer is Yes")


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Приступим :)")


@bot.message_handler(commands=['hello'])
def hello_message(message):
	bot.send_message(message.chat.id,"Привет, {0.first_name}! ✌️ ".format(message.from_user), reply_markup = markup_ex)


@bot.message_handler(commands=['report'])
def report_message(message):
	bot.send_message(message.chat.id,"Вот твой отчет")


def privet(message):
	return message.text == 'Привет'

@bot.message_handler(func = privet)
def message_message(message):
	bot.send_message(message.chat.id,"И вам не хворать")

#----------------------------------------------------------------------------

bot.infinity_polling()


# ШПАРГАЛКИ

	# bot.reply_to(message=message, text=str(message.chat.id))
	# markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# item1 = types.KeyboardButton('Отжимания')
	# item2 = types.KeyboardButton('Приседания')
	# item3 = types.KeyboardButton('Икры')
	# item4 = types.KeyboardButton('Пресс')
	# markup.add(item1, item2, item3, item4)