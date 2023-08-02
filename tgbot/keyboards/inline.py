import configparser
import telebot
from telebot import types
import psycopg2


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("purchase/settings.ini")  # читаем конфиг
# обращаемся как к обычному словарю!
token = config['Telegram']['token'] 
pg_dbname = config['Postgres']['pg_dbname']
pg_user = config['Postgres']['pg_user']
pg_userpass = config['Postgres']['pg_userpass']
pg_host = config['Postgres']['pg_host']
pg_port = config['Postgres']['pg_port']

t_exercises='exercises' # таблица БД "список упражнений"

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