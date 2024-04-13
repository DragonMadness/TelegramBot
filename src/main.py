from typing import Callable

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, Message, CallbackQuery
from requests.exceptions import ConnectTimeout

from pathlib import Path
from src.util import messages
from src.util.paged_message_manager import PagedMessageManager
from src.logging.logger import Logger
from src.logging.log_level import *

from src.manager.question_manager import QuestionManager
from src.manager.user_manager import UserManager
from src.model.question import Question
from src.model.response import Response
from src.model.user import User

RESOURCES_PATH = Path.cwd().absolute() / "resources"
QUESTIONS_STORAGE_PATH = RESOURCES_PATH / "storage" / "questions.json"
USERS_STORAGE_PATH = RESOURCES_PATH / "storage" / "users.json"
TOKEN_PATH = RESOURCES_PATH / "token.txt"

logger = Logger(print)
logger.log(INFO, "Logger created.")

bot = telebot.TeleBot(open(TOKEN_PATH).read())
while True:
    try:
        bot.delete_my_commands()
        bot.set_my_commands(commands=[
            BotCommand("/start", "Описание бота"),
            BotCommand("/settings", "Пользовательские настройки"),
            BotCommand("/question", "Создаёт новый вопрос"),
            BotCommand("/myquestions", "Список заданных вами вопросов"),
            BotCommand("/allquestions", "Список заданных вопросов"),
            BotCommand("/help", "Выводит подсказку по командам")
        ])
        break
    except ConnectTimeout:
        logger.log(ERR, "Timed out while connecting to Telegram API. Retrying")

waiting_reply: dict[User: Callable] = {}
user_manager = UserManager()
user_manager.read(USERS_STORAGE_PATH)
question_manager = QuestionManager()
question_manager.read(QUESTIONS_STORAGE_PATH, user_manager)
paged_message_manager = PagedMessageManager()


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.from_user.id, messages.greeting)


@bot.message_handler(commands=["settings"])
def settings(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)

    markup = InlineKeyboardMarkup(keyboard=[
        [InlineKeyboardButton("Уведомления", callback_data="I")],
        [InlineKeyboardButton(("✅" if user.do_notify_new_questions() else "❌") + " Новые вопросы", callback_data="NQ"),
         InlineKeyboardButton(("✅" if user.do_notify_new_answers() else "❌") + " Новые ответы", callback_data="NR")]])

    bot.send_message(user.get_userid(), messages.settings, reply_markup=markup)


@bot.message_handler(commands=["question"])
def new_question_request(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)

    if user not in waiting_reply.keys():
        waiting_reply[user] = create_question

    bot.send_message(user.get_userid(), messages.request_question)


@bot.message_handler(commands=["myquestions"])
def get_user_questions(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)

    user_questions = question_manager.get_questions_for_user(user)
    if len(user_questions) == 0:
        bot.send_message(user.get_userid(), messages.no_questions_asked)
        return

    message_text, markup = paged_message_manager.get_message(user.get_userid(), user_questions)
    if message_text is None or markup is None:
        return
    markup.row(InlineKeyboardButton("Добавить ответ", callback_data="RA"))
    markup.row(InlineKeyboardButton("Просмотреть ответы", callback_data="RV"))
    bot.send_message(user.get_userid(), message_text, reply_markup=markup)


@bot.message_handler(commands=["allquestions"])
def get_all_questions(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)

    questions = question_manager.get_questions()
    if len(questions) == 0:
        bot.send_message(user.get_userid(), messages.no_questions_asked)
        return

    message_text, markup = paged_message_manager.get_message(user.get_userid(), questions)
    if message_text is None or markup is None:
        return
    markup: InlineKeyboardMarkup
    markup.row(InlineKeyboardButton("Добавить ответ", callback_data="RA"))
    markup.row(InlineKeyboardButton("Просмотреть ответы", callback_data="RV"))
    bot.send_message(user.get_userid(), message_text, reply_markup=markup)


@bot.message_handler(commands=["stop"])
def stop(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)

    question_manager.save(QUESTIONS_STORAGE_PATH)
    user_manager.save(QUESTIONS_STORAGE_PATH)

    bot.send_message(user.get_userid(), messages.shutdown)
    bot.stop_polling()


@bot.message_handler(commands=["help"])
def show_help(message: Message):
    bot.send_message(message.from_user.id, messages.help_message)


@bot.message_handler(content_types=["text"])
def on_text(message: Message):
    text = message.text
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)

    if "/" in text[0]:
        if user in waiting_reply.keys():
            waiting_reply.pop(user)
        return

    if user in waiting_reply.keys():
        waiting_reply.pop(user)(message)


@bot.callback_query_handler(lambda x: x)
def handle_callback(callback: CallbackQuery):
    user = user_manager.compute_if_not_exists(callback.from_user.id, callback.from_user.username)
    action = callback.data.split(";")[0]
    message = callback.message
    if action[0] == "I":
        return
    elif action[0] == "P":
        paged_message_manager.handle_callback(callback.data)
        new_message_text, new_markup = paged_message_manager.get_message(user.get_userid())
        if new_message_text is None or new_markup is None:
            return
        new_markup: InlineKeyboardMarkup

        keyboard = message.reply_markup.keyboard.copy()
        keyboard[0] = new_markup.keyboard[0]

        if new_message_text == message.text and message.reply_markup.keyboard == keyboard:
            return

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=new_message_text,
                              reply_markup=InlineKeyboardMarkup(keyboard=keyboard))
    elif action[0] == "R":
        if user.get_userid() not in paged_message_manager.object_lists_cache.keys():
            return
        user_pages_data = paged_message_manager.object_lists_cache[user.get_userid()]
        if action == "RA":
            if not isinstance(user_pages_data[0][0], Question):
                return
            waiting_reply[user] = add_answer
            bot.send_message(user.get_userid(), messages.request_reply)
        elif action == "RV":
            if not isinstance(user_pages_data[0][0], Question):
                return
            current_question: Question = user_pages_data[0][user_pages_data[1]]

            if len(current_question.get_responses()) == 0:
                bot.send_message(user.get_userid(), messages.no_responses)
                return

            message_text, markup = paged_message_manager.get_message(user.get_userid(), current_question.get_responses())
            markup: InlineKeyboardMarkup
            markup.row(InlineKeyboardButton("⬆", callback_data="RU"),
                       InlineKeyboardButton("⬇", callback_data="RD"))

            bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=message_text, reply_markup=markup)
        elif action == "RU":
            if not isinstance(user_pages_data[0][0], Response):
                return
            current_response: Response = user_pages_data[0][user_pages_data[1]]
            current_response.add_rating()

            keyboard = message.reply_markup.keyboard.copy()
            message_text, markup = paged_message_manager.get_message(user.get_userid())
            keyboard[0] = markup.keyboard[0]
            new_markup = InlineKeyboardMarkup(keyboard=keyboard)

            bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                                  text=message_text, reply_markup=new_markup)

            logger.info("User upvoted a repsonse")
        elif action == "RD":
            user_pages_data = paged_message_manager.object_lists_cache[user.get_userid()]
            if not isinstance(user_pages_data[0][0], Response):
                return
            current_response: Response = user_pages_data[0][user_pages_data[1]]
            current_response.deduct_rating()

            keyboard = message.reply_markup.keyboard.copy()
            message_text, markup = paged_message_manager.get_message(user.get_userid())
            keyboard[0] = markup.keyboard[0]
            new_markup = InlineKeyboardMarkup(keyboard=keyboard)

            bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                                  text=message_text, reply_markup=new_markup)

            logger.info("User downvoted a repsonse")
    elif action[0] == "N":
        if action == "NQ":
            user.set_notify_new_questions(not user.do_notify_new_questions())
        elif action == "NR":
            user.set_notify_new_answers(not user.do_notify_new_answers())
        markup = InlineKeyboardMarkup(keyboard=[
            [InlineKeyboardButton("Уведомления", callback_data="I")],
            [InlineKeyboardButton(("✅" if user.do_notify_new_questions() else "❌") + " Новые вопросы",
                                  callback_data="NQ"),
             InlineKeyboardButton(("✅" if user.do_notify_new_answers() else "❌") + " Новые ответы",
                                  callback_data="NR")]])
        bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=markup)


def create_question(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)
    username = message.from_user.username

    question_manager.new_question(user, message.text)
    for elem in user_manager.get_notifiable_users():
        if elem == user:
            continue
        bot.send_message(elem.get_userid(), messages.new_question)
    bot.send_message(user.get_userid(), messages.question_saved)
    logger.log(INFO, f"Successfully registered a question from {username}")


def add_answer(message: Message):
    user = user_manager.compute_if_not_exists(message.from_user.id, message.from_user.username)
    if user.get_userid() not in paged_message_manager.object_lists_cache.keys():
        return

    user_pages_data = paged_message_manager.object_lists_cache[user.get_userid()]

    current_question: Question = user_pages_data[0][user_pages_data[1]]
    current_question.add_response(user, message.text)

    if current_question.get_author().do_notify_new_answers() and current_question.get_author() != user:
        bot.send_message(current_question.get_author().get_userid(), messages.new_response)

    bot.send_message(user.get_userid(), messages.reply_saved)


logger.log(INFO, "Bot started!")
bot.polling(non_stop=True, interval=0)
paged_message_manager.destroy()
question_manager.save(QUESTIONS_STORAGE_PATH)
user_manager.save(USERS_STORAGE_PATH)
logger.log(INFO, "Bot shut down.")
