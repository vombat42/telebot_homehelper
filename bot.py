import configparser
import telebot
import psycopg2
from tgbot.keyboards import *
from telebot import types
from datetime import date



# import logging

# from tgbot.config import load_config
# from tgbot.filters.admin import AdminFilter
# from tgbot.handlers.admin import register_admin
# from tgbot.handlers.echo import register_echo
# from tgbot.handlers.user import register_user
# from tgbot.middlewares.environment import EnvironmentMiddleware


#----------------------------------------------------------------------------

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("purchase/settings.ini")  # читаем конфиг
# обращаемся как к обычному словарю!
token = config['Telegram']['token'] 
pg_dbname = config['Postgres']['pg_dbname']
pg_user = config['Postgres']['pg_user']
pg_userpass = config['Postgres']['pg_userpass']
pg_host = config['Postgres']['pg_host']
pg_port = config['Postgres']['pg_port']

#----------------------------------------------------------------------------

bot=telebot.TeleBot(token)


bot.set_my_commands(menu)

@bot.message_handler(commands=['exercise'])
def exercises_list(message):
    mess = bot.send_message(message.chat.id, 'Нажимай на упражнение и потом вводи количество', reply_markup = markup_ex)

# print('-----A-------')

#----------------------------------------------------------------------------

bot.infinity_polling()
