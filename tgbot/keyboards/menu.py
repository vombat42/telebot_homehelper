import telebot
from telebot import types

menu = [
	telebot.types.BotCommand("/start", "Перезапуск бота"),
    telebot.types.BotCommand("/hello", "✋ приветствие"),
    telebot.types.BotCommand("/exercise", "🏋 упражнения"),
    telebot.types.BotCommand("/report", "📜 отчет"),
    telebot.types.BotCommand("/graph", "📊 график"),
    telebot.types.BotCommand("/help", "Помощь")
]
    