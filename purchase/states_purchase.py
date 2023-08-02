import configparser
import telebot
from telebot import types
import psycopg2
from datetime import date


#----------------------------------------------------------------------------

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
# обращаемся как к обычному словарю!
token = config['Telegram']['token'] 
pg_dbname = config['Postgres']['pg_dbname']
pg_user = config['Postgres']['pg_user']
pg_userpass = config['Postgres']['pg_userpass']
pg_host = config['Postgres']['pg_host']
pg_port = config['Postgres']['pg_port']

#----------------------------------------------------------------------------

bot=telebot.TeleBot(token)

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Перезапуск бота"),
    telebot.types.BotCommand("/exercise", "🏋 упражнения"),
    telebot.types.BotCommand("/report", "📜 отчет"),
    telebot.types.BotCommand("/graph", "📊 график"),
    telebot.types.BotCommand("/hello", "✋ приветствие"),
    telebot.types.BotCommand("/help", "Помощь")
])

t_exercises='exercises' # таблица БД "список упражнений"
t_events='events' # таблица БД "события (выполненные упражнения)"
message_list=[] # список id сообщений диалога текущего состояния
current_mess_id = 0 # id главного сообщения текущего диалога
exercise_id = -1
exercise_count = 0

# формируем клавиатуру с упражнениями
conn = psycopg2.connect(f'postgresql://{pg_user}:{pg_userpass}@{pg_host}:{pg_port}/{pg_dbname}')
conn.autocommit = True
cur = conn.cursor()
cur.execute(
   f"SELECT id, ex_name, ex_unit FROM {t_exercises};"
)
buttons=cur.fetchall()
cur.close()
conn.close()
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
markup_ex.row(types.InlineKeyboardButton(text='В главное меню', callback_data='-2'))

# формируем клавиатуру подтверждения ввода
markup_yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1=types.KeyboardButton(text="Записать")
item2=types.KeyboardButton(text="Отменить")
markup_yes_no.add(item1, item2)

# Определяем состояния FSM
states = {
   'choose_exercise': 0,
   'enter_count': 1,
   'confirm': 2,
}
ex_states = [0,1,2] # состояния диалога "Упражнения"

# Определяем переменную для хранения текущего состояния пользователя
current_state = {}

#----------------------------------------------------------------------------

# кто не в списке userlist - проходит мимо
userlist=(406827859,)
@bot.message_handler(func=lambda message: message.chat.id not in userlist)
def some(message):
   bot.send_message(message.chat.id, "Sorry...")

#----------------------------------------------------------------------------

def db_events_add(chat_id, ex_id, ex_count, ex_date):
	conn = psycopg2.connect(f'postgresql://{pg_user}:{pg_userpass}@{pg_host}:{pg_port}/{pg_dbname}')
	conn.autocommit = True
	cur = conn.cursor()
	cur.execute(f"SELECT id FROM users WHERE chat_id='{chat_id}';")
	user_id=cur.fetchone()[0]
	cur.execute(
	   f"INSERT INTO {t_events} (date_enent, user_id, ex_id, ex_count) VALUES ('{ex_date}',{user_id},{ex_id},{ex_count});"
	)
	cur.close()
	conn.close()


def del_mess_from_mess_list(message):
	global message_list, current_mess_id
	for i in message_list:
		bot.delete_message(chat_id=message.chat.id, message_id=i)
	message_list.clear()
	if current_mess_id != 0:
		bot.delete_message(chat_id=message.chat.id, message_id=current_mess_id)

# обработка выбора пользователем "Упражнения"
@bot.message_handler(commands=['exercise'])
def exercises_list(message):
	global message_list, ex_states
	if current_state.get(message.chat.id) in ex_states:
		bot.delete_message(message.chat.id, message.id)
		return
	mess = bot.send_message(message.chat.id, 'Нажимай на упражнение и потом вводи количество', reply_markup = markup_ex)
	message_list.append(mess.id)
	current_state[message.chat.id] = states['choose_exercise']

@bot.callback_query_handler(func=lambda call: True)
def choose_exercise(call):
	global current_mess_id, exercise_id, exercise_count, message_list
	if call.data == '-2': # выход в главное меню
		bot.answer_callback_query(call.id, f'Выход в главное меню')
		bot_message = f'Введите количество <b>{buttons[exercise_id][1]}({buttons[exercise_id][2]})</b>'
		mess = bot.send_message(call.message.chat.id, 'главное меню')
		current_state[call.message.chat.id] = -1
		del_mess_from_mess_list(call.message)
		return
	if call.data == '-1': # выходим, если нажата пустая кнопка
		bot.answer_callback_query(call.id, f'Нажата пустая кнопка')
		return
	if current_state[call.message.chat.id] != states['choose_exercise']: # если другое состояние диалога
		if current_state[call.message.chat.id] == states['enter_count']: # пользователь меняет упражнение вместо ввода количества
			bot.delete_message(call.message.chat.id, current_mess_id)
		else:
			bot.answer_callback_query(call.id, f'Сейчас другое состояние диалога')
			return
	exercise_id = int(call.data)
	bot_message = f'Введите количество <b>{buttons[exercise_id][1]}({buttons[exercise_id][2]})</b>'
	mess = bot.send_message(call.message.chat.id, bot_message, parse_mode='HTML')
	current_mess_id = mess.id
	current_state[call.message.chat.id] = states['enter_count']
	bot.answer_callback_query(call.id, f'Вы выбрали {buttons[exercise_id][1]}')


# пользователь вводит произвольное сообщение вместо выбора упражнения - просто удаляяем это сообщение
@bot.message_handler(func=lambda message: current_state.get(message.chat.id) == states['choose_exercise'])
def del_mess(message):
	bot.delete_message(chat_id=message.chat.id, message_id=message.id)


# пользователь вводит количество выполненных упражнений
@bot.message_handler(func=lambda message: current_state.get(message.chat.id) == states['enter_count'])
def count_exercise(message):
	global current_mess_id, exercise_id, exercise_count
	if message.text.isdigit(): #проверяем, что введено число
		count = int(message.text)
		if count > 0:
			bot_message = f'Записать <b><u>{buttons[exercise_id][1]} - {count} {buttons[exercise_id][2]}</u></b> ?'
			bot.delete_message(chat_id=message.chat.id, message_id=current_mess_id)
			mess = bot.send_message(message.chat.id, bot_message, parse_mode='HTML', reply_markup = markup_yes_no)
			current_mess_id = mess.id
			exercise_count = count
			current_state[message.chat.id] = states['confirm']
	bot.delete_message(message.chat.id, message.id)

# подтверждение записи в базу и запись в базу
@bot.message_handler(func=lambda message: current_state.get(message.chat.id) == states['confirm'])
def record_event(message):
	global current_mess_id, exercise_id, exercise_count 
	if message.text == 'Записать':
		exercise_date = str(date.today())
		db_events_add(message.chat.id, buttons[exercise_id][0], exercise_count, exercise_date)
		bot_message  = f'<b><u>Записано</u></b> : {buttons[exercise_id][1]} - {exercise_count} {buttons[exercise_id][2]} !'
		bot.delete_message(chat_id=message.chat.id, message_id=current_mess_id)
		mess = bot.send_message(message.chat.id, bot_message, parse_mode='HTML')
		current_mess_id = 0
		current_state[message.chat.id] = states['choose_exercise']
	elif message.text == 'Отменить':
		bot_message = f'Введите количество <b>{buttons[exercise_id][1]}({buttons[exercise_id][2]})</b>'
		bot.delete_message(chat_id=message.chat.id, message_id=current_mess_id)
		mess = bot.send_message(message.chat.id, bot_message, parse_mode='HTML')
		current_mess_id = mess.id
		current_state[message.chat.id] = states['enter_count']
	else:
		bot_message = f'Записать <b><u>{buttons[exercise_id][1]} - {exercise_count} {buttons[exercise_id][2]}</u></b> ?'
		bot.delete_message(chat_id=message.chat.id, message_id=current_mess_id)
		mess = bot.send_message(message.chat.id, bot_message, parse_mode='HTML', reply_markup = markup_yes_no)
		current_mess_id = mess.id
	bot.delete_message(message.chat.id, message.id)


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Приступим :)")


@bot.message_handler(commands=['hello'])
def hello_message(message):
	global user_enter_id
	bot.send_message(message.chat.id,"Привет, {0.first_name}! ✌️ ".format(message.from_user))


@bot.message_handler(commands=['report'])
def report_message(message):
	bot.send_message(message.chat.id,"Вот твой отчет")


@bot.message_handler(commands=['graph'])
def graph_message(message):
	bot.send_message(message.chat.id,"📊")


def privet(message):
	return message.text == 'Привет'

@bot.message_handler(func = privet)
def message_1(message):
	bot.send_message(message.chat.id,"И вам не хворать")


#----------------------------------------------------------------------------

bot.infinity_polling()
