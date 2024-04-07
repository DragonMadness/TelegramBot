import telebot
from telebot import types

import messages
from logger import Logger
from log_level import *

bot = telebot.TeleBot(open("./token.txt").read())
logger = Logger(print)
logger.log(INFO, "Logger created.")


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Задать вопрос"),
        types.KeyboardButton("Мои вопросы"),
        types.KeyboardButton("Поиск"))

    bot.send_message(message.from_user.id, messages.greeting, reply_markup=markup)


logger.log(INFO, "Bot started!")
bot.polling(non_stop=True, interval=0)
