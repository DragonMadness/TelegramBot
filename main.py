import telebot
from telebot.types import *
from requests.exceptions import ConnectTimeout

import messages
from logger import Logger
from log_level import *

from question import Question

logger = Logger(print)
logger.log(INFO, "Logger created.")

bot = telebot.TeleBot(open("./token.txt").read())
while True:
    try:
        bot.delete_my_commands()
        break
    except ConnectTimeout:
        logger.log(WARN, "Timed out while connecting to Telegram API. Retrying")
bot.set_my_commands(commands=[
    BotCommand("/start", "Описание бота"),
    BotCommand("/question", "Создаёт новый вопрос"),
    BotCommand("/myquestions", "Список заданных вами вопросов.")
])

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


@bot.message_handler(commands=["myquestions"])
def get_user_questions(message: Message):
    userid = message.from_user.id

    user_questions = [question.get_formatted() for question in questions if question.get_poster_id() == userid]
    if len(user_questions) == 0:
        bot.send_message(userid, messages.no_questions_asked)
        return
    bot.send_message(userid, "\n\n".join(user_questions))


@bot.message_handler(content_types=["text"])
def new_question_creation(message: Message):
    text = message.text
    userid = message.from_user.id
    if text != "/question":
        new_questions_from.remove(userid)
    if "/" in text:
        return

    if userid in new_questions_from:
        questions.append(Question(userid, message.from_user.username, text))
        bot.send_message(userid, messages.question_saved)


logger.log(INFO, "Bot started!")
bot.polling(non_stop=True, interval=0)
