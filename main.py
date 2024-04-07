import telebot
from telebot import types

bot = telebot.TeleBot(open("./token.txt").read())


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("Задать вопрос"),
        types.KeyboardButton("Мои вопросы"),
        types.KeyboardButton("Поиск"))

    bot.send_message(message.from_user.id, "Привет, это MechOverflow! 👋\n"
                                           "Через меня ты можешь задать вопрос другим пользователям "
                                           "или ответить на чужой вопрос. Я позволяю машиностроителям "
                                           "помогать друг другу и делиться знаниями. 📚\n"
                                           "\n"
                                           "Ты можешь использовать кнопки ниже,\n"
                                           "чтобы воспользоваься моими возможностями. 🔘\n"
                                           ""
                                           "Приятного пользования!\n", reply_markup=markup)


bot.polling(none_stop=True, interval=0)
