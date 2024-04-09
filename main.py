import telebot
from telebot.types import *
from requests.exceptions import ConnectTimeout

import messages
from logger import Logger
from log_level import *

from question_manager import QuestionManager

logger = Logger(print)
logger.log(INFO, "Logger created.")

bot = telebot.TeleBot(open("./token.txt").read())
while True:
    try:
        bot.delete_my_commands()
        bot.set_my_commands(commands=[
            BotCommand("/start", "Описание бота"),
            BotCommand("/question", "Создаёт новый вопрос"),
            BotCommand("/myquestions", "Список заданных вами вопросов."),
            BotCommand("/allquestions", "Список заданных вопросов."),
            BotCommand("/stop", "Останавливает бота, сохраняя данные локально.")
        ])
        break
    except ConnectTimeout:
        logger.log(WARN, "Timed out while connecting to Telegram API. Retrying")

STORAGE_PATH = Path.cwd().absolute() / "storage" / "questions.json"
new_questions_from = []
question_manager = QuestionManager()
question_manager.read(STORAGE_PATH)


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

    user_questions = [question.get_formatted() for question in question_manager.get_questions_for_user(userid)]
    if len(user_questions) == 0:
        bot.send_message(userid, messages.no_questions_asked)
        return
    bot.send_message(userid, "\n\n".join(user_questions))


# @bot.message_handler(commands=["allquestions"])
# def get_user_questions(message: Message):
#     userid = message.from_user.id
#
#     user_questions = [question.get_formatted() for question in question_manager.get_questions()]
#     if len(user_questions) == 0:
#         bot.send_message(userid, messages.no_questions_asked)
#         return
#     bot.send_message(userid, "\n\n".join(user_questions))


@bot.message_handler(commands=["stop"])
def stop(message: Message):
    userid = message.from_user.id

    question_manager.save(STORAGE_PATH)

    bot.send_message(userid, messages.shutdown)
    bot.stop_polling()


@bot.message_handler(content_types=["text"])
def new_question_creation(message: Message):
    text = message.text
    userid = message.from_user.id
    username = message.from_user.username
    if "/" in text:
        if userid in new_questions_from:
            new_questions_from.remove(userid)
        return

    if userid in new_questions_from:
        question_manager.new_question(userid, username, text)
        bot.send_message(userid, messages.question_saved)
        logger.log(INFO, f"Successfully registered a question from {username}")


logger.log(INFO, "Bot started!")
bot.polling(non_stop=True, interval=0)
logger.log(INFO, "Bot shut down.")
