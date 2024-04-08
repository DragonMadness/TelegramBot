import telebot
from telebot.types import *

import messages
from logger import Logger
from log_level import *

from question import Question

bot = telebot.TeleBot(open("./token.txt").read())
bot.set_my_commands(commands=[
    BotCommand("/start", "Описание бота"),
    BotCommand("/question", "Создаёт новый вопрос")
])

logger = Logger(print)
logger.log(INFO, "Logger created.")

new_questions_from = []
questions = []


@bot.message_handler(commands=["start"])
def start(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/question", "/my-questions", "/search")

    bot.send_message(message.from_user.id, messages.greeting, reply_markup=markup)


@bot.message_handler(commands=["question"])
def new_question_request(message: Message):
    userid = message.from_user.id

    if userid not in new_questions_from:
        new_questions_from.append(message.from_user.id)

    bot.send_message(message.from_user.id, messages.request_question)


@bot.message_handler(content_types=["text"])
def new_question_creation(message: Message):
    text = message.text
    if "/" in text:
        return
    userid = message.from_user.id

    if userid in new_questions_from:
        questions.append(Question(text))
        bot.send_message(userid, messages.question_saved)


logger.log(INFO, "Bot started!")
bot.polling(non_stop=True, interval=0)
