import configparser
import telebot
from telebot import types
import psycopg2

#----------------------------------------------------------------------------

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
# обращаемся как к обычному словарю!
token = config['Telegram']['token'] 
config.read("settings.ini")  # читаем конфиг
pg_dbname = config['Postgres']['pg_dbname']
pg_user = config['Postgres']['pg_user']
pg_userpass = config['Postgres']['pg_userpass']
pg_host = config['Postgres']['pg_host']
pg_port = config['Postgres']['pg_port']

#----------------------------------------------------------------------------

bot=telebot.TeleBot(token)
t_exercises='exercises'
user_enter_id=0 # id сообщения о вводе количества упражнений

conn = psycopg2.connect(f'postgresql://{pg_user}:{pg_userpass}@{pg_host}:{pg_port}/{pg_dbname}')
conn.autocommit = True
cur = conn.cursor()
cur.execute(
   f"SELECT id, ex_name, ex_unit FROM {t_exercises};"
)


# формируем клавиатуру с упражнениями
buttons=cur.fetchall()
cur.close()
conn.close()
# buttons=('Отжимания','Икры','Пресс','Приседания','Планка','Наклоны','Спина','Шея')
markup_ex = types.InlineKeyboardMarkup(row_width=3)
for i in range(0,len(buttons), 3):
	if len(buttons)-i>=3:
		item1=types.InlineKeyboardButton(text=buttons[i][1], callback_data=str(i))
		item2=types.InlineKeyboardButton(text=buttons[i+1][1], callback_data=str(i+1))
		item3=types.InlineKeyboardButton(text=buttons[i+2][1], callback_data=str(i+2))
	elif len(buttons)-i==2:
		item1=types.InlineKeyboardButton(text=buttons[i][1], callback_data=str(i))
		item2=types.InlineKeyboardButton(text=buttons[i+1][1], callback_data=str(i+1))
		item3=types.InlineKeyboardButton(text=' ', callback_data='-1')
	elif len(buttons)-i==1:
		item1=types.InlineKeyboardButton(text=buttons[i][1], callback_data=str(i))
		item2=types.InlineKeyboardButton(text=' ', callback_data='-1')
		item3=types.InlineKeyboardButton(text=' ', callback_data='-1')
	markup_ex.add(item1, item2, item3)

# markup_yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
markup_yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1=types.KeyboardButton(text="Записать")
item2=types.KeyboardButton(text="Отменить")
markup_yes_no.add(item1, item2)
#----------------------------------------------------------------------------

# кто не в списке userlist - проходит мимо
userlist=(406827859,)
# @bot.message_handler(func=lambda message: message.chat.id not in userlist)
# def some(message):
#    bot.send_message(message.chat.id, "Sorry...")

#----------------------------------------------------------------------------


# обработка выбора пользователем "Упражнения"
@bot.callback_query_handler(func=lambda call: True)
def check_callback(call):
	global user_enter_id
	if call.data!='-1':
		enter_message = f'Введите количество <b>{buttons[int(call.data)][1]}({buttons[int(call.data)][2]})</b>'
		if user_enter_id!=0:
			mess = bot.edit_message_text(chat_id=call.message.chat.id, message_id=user_enter_id, text=enter_message, parse_mode='HTML')
			bot.register_next_step_handler(mess, enter_events, int(call.data))
		else:
			mess = bot.send_message(call.message.chat.id, enter_message, parse_mode='HTML')
			user_enter_id = mess.id
			bot.register_next_step_handler(mess, enter_events, int(call.data))
	bot.answer_callback_query(call.id, "Answer is Yes")

# пользователь вводит количество выполненных упражнений
def enter_events(message, i):
	global user_enter_id
	mess_id=message.id
	if message.text.isdigit(): #проверяем, что введено число
		count = int(message.text)
		if count > 0:
			enter_message = f'Записать <b><u>{buttons[i][1]} - {count} {buttons[i][2]}</u></b> ?'
			bot.delete_message(chat_id=message.chat.id, message_id=user_enter_id)
			mess = bot.send_message(chat_id=message.chat.id, text=enter_message, parse_mode='HTML', reply_markup = markup_yes_no)
			user_enter_id = mess.id
			bot.register_next_step_handler(mess, record_event, i, count)
		else: #если введен 0, то повторяем ввод
			bot.register_next_step_handler(message, enter_events, i)
	else: #если введено не число, то повторяем ввод
		bot.register_next_step_handler(message, enter_events, i)
	bot.delete_message(message.chat.id, mess_id)

# подтверждение записи в базу и запись в базу
def record_event(message, i, count):
	global user_enter_id
	if message.text == 'Записать':
		mess = f'<b><u>Записано</u></b> : {buttons[i][1]} - {count} {buttons[i][2]} !'
		bot.delete_message(message.chat.id, message.id)
		if user_enter_id!=message.id:
			bot.delete_message(message.chat.id, user_enter_id)
		bot.send_message(message.chat.id, mess, parse_mode='HTML')
		user_enter_id = 0
	elif message.text == 'Отменить':
		bot.delete_message(message.chat.id, message.id)
		if user_enter_id!=message.id:
			bot.delete_message(message.chat.id, user_enter_id)
		user_enter_id = 0
	else: # если пользователь не нажал кнопку, а ввел какое-то сообщение, то повторяем
		bot.delete_message(message.chat.id, message.id)
		if user_enter_id!=message.id:
			bot.delete_message(message.chat.id, user_enter_id)
		enter_message = f'Записать <b><u>{buttons[i][1]} - {count} {buttons[i][2]}</u></b> ?'
		mess1 = bot.send_message(chat_id=message.chat.id, text=enter_message, parse_mode='HTML', reply_markup = markup_yes_no)
		user_enter_id = mess1.id
		bot.register_next_step_handler(mess1, record_event, i, count)


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Приступим :)")

@bot.message_handler(commands=['hello'])
def hello_message(message):
	global user_enter_id
	bot.send_message(message.chat.id,"Привет, {0.first_name}! ✌️ ".format(message.from_user))


@bot.message_handler(commands=['graph'])
def hello_message(message):
	global user_enter_id
	bot.send_message(message.chat.id, 'Нажимай на упражнение и потом вводи количество', reply_markup = markup_ex)
	user_enter_id = 0


@bot.message_handler(commands=['report'])
def report_message(message):
	bot.send_message(message.chat.id,"Вот твой отчет")


def privet(message):
	return message.text == 'Привет'

@bot.message_handler(func = privet)
def message_1(message):
	bot.send_message(message.chat.id,"И вам не хворать")


#----------------------------------------------------------------------------

bot.infinity_polling()


# ШПАРГАЛКИ

# @bot.message_handler(func = lambda message: True)
# def message_true(message):
# 	global user_enter_id
# 	if message.text == 'Записать':
# 		bot.delete_message(message.chat.id, user_enter_id)
# 		bot.delete_message(message.chat.id, message.id)
# 		user_enter_id = 0
# 		bot.send_message(message.chat.id, f'<b><u>Записано</u></b>', parse_mode='HTML')

	# bot.reply_to(message=message, text=str(message.chat.id))
	# markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# item1 = types.KeyboardButton('Отжимания')
	# item2 = types.KeyboardButton('Приседания')
	# item3 = types.KeyboardButton('Икры')
	# item4 = types.KeyboardButton('Пресс')
	# markup.add(item1, item2, item3, item4)