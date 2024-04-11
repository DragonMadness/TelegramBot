from typing import Callable

import telebot
from telebot.types import *
from requests.exceptions import ConnectTimeout

from src.util import messages
from src.util.paged_message_manager import PagedMessageManager
from src.logging.logger import Logger
from src.logging.log_level import *

from src.manager.question_manager import QuestionManager

RESOURCES_PATH = Path.cwd().absolute() / "resources"
STORAGE_PATH = RESOURCES_PATH / "storage" / "questions.json"
TOKEN_PATH = RESOURCES_PATH / "token.txt"

logger = Logger(print)
logger.log(INFO, "Logger created.")

bot = telebot.TeleBot(open(TOKEN_PATH).read())
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

waiting_reply: dict[int: Callable] = {}
question_manager = QuestionManager()
question_manager.read(STORAGE_PATH)
paged_message_manager = PagedMessageManager()


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.from_user.id, messages.greeting, parse_mode="Markdown")


@bot.message_handler(commands=["question"])
def new_question_request(message: Message):
    userid = message.from_user.id

    if userid not in waiting_reply.keys():
        waiting_reply[userid] = create_question

    bot.send_message(message.from_user.id, messages.request_question, parse_mode="Markdown")


@bot.message_handler(commands=["myquestions"])
def get_user_questions(message: Message):
    userid = message.from_user.id

    user_questions = question_manager.get_questions_for_user(userid)
    if len(user_questions) == 0:
        bot.send_message(userid, messages.no_questions_asked, parse_mode="Markdown")
        return

    message_text, markup = paged_message_manager.get_message(userid, user_questions)
    if message_text is None or markup is None:
        return
    markup.row(InlineKeyboardButton("Добавить ответ", callback_data="RA"))
    bot.send_message(userid, message_text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["allquestions"])
def get_all_questions(message: Message):
    userid = message.from_user.id

    questions = question_manager.get_questions()
    if len(questions) == 0:
        bot.send_message(userid, messages.no_questions_asked, parse_mode="Markdown")
        return

    message_text, markup = paged_message_manager.get_message(userid, questions)
    if message_text is None or markup is None:
        return
    markup: InlineKeyboardMarkup
    markup.row(InlineKeyboardButton("Добавить ответ", callback_data="RA"))
    bot.send_message(userid, message_text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(commands=["stop"])
def stop(message: Message):
    userid = message.from_user.id

    question_manager.save(STORAGE_PATH)

    bot.send_message(userid, messages.shutdown, parse_mode="Markdown")
    bot.stop_polling()


@bot.message_handler(commands=["help"])
def show_help(message: Message):
    bot.send_message(message.from_user.id, messages.help_message, parse_mode="Markdown")


@bot.message_handler(content_types=["text"])
def on_text(message: Message):
    text = message.text
    userid = message.from_user.id
    if "/" in text:
        if userid in waiting_reply.keys():
            waiting_reply.pop(userid)
        return

    if userid in waiting_reply.keys():
        waiting_reply.pop(userid)(message)


@bot.callback_query_handler(lambda x: x)
def handle_callback(callback: CallbackQuery):
    userid = callback.from_user.id
    action = callback.data.split(";")[0]
    message = callback.message
    if action[0] == "P":
        paged_message_manager.handle_callback(callback.data)
        new_message_text, new_markup = paged_message_manager.get_message(userid)
        if new_message_text is None or new_markup is None:
            return
        new_markup: InlineKeyboardMarkup

        keyboard = message.reply_markup.keyboard.copy()
        keyboard[0] = new_markup.keyboard[0]

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=new_message_text,
                              reply_markup=InlineKeyboardMarkup(keyboard=keyboard))
    elif action == "RA":
        if userid not in paged_message_manager.object_lists_cache.keys():
            return
        waiting_reply[userid] = add_answer
        bot.send_message(userid, messages.request_reply)


def create_question(message: Message):
    userid = message.from_user.id
    username = message.from_user.username

    question_manager.new_question(userid, username, message.text)
    bot.send_message(userid, messages.question_saved, parse_mode="Markdown")
    logger.log(INFO, f"Successfully registered a question from {username}")


def add_answer(message: Message):
    question_manager.get_questions()


logger.log(INFO, "Bot started!")
bot.polling(non_stop=True, interval=0)
paged_message_manager.destroy()
logger.log(INFO, "Bot shut down.")
