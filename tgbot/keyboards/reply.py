from telebot import types

# формируем клавиатуру подтверждения ввода
markup_yes_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1=types.KeyboardButton(text="Записать")
item2=types.KeyboardButton(text="Отменить")
markup_yes_no.add(item1, item2)