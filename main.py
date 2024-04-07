import telebot

bot = telebot.TeleBot(open("./token.txt").read())


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.from_user.id, "Мяу")


bot.polling(none_stop=True, interval=0)
