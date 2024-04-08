from response import Response
from telebot.types import User


class Question:
    def __init__(self, poster_id: int, poster_name: str, question_text: str, responses: list[Response] = ()):
        self.__poster_id = poster_id
        self.__poster_name = poster_name
        self.__question_text = question_text
        self.__responses: list[Response] = responses

    def get_poster_id(self):
        return self.__poster_id

    def get_text(self):
        return self.__question_text

    def get_formatted(self):
        output = (f"Вопрос пользователя @{self.__poster_name}.\n\n"
                  f"{self.__question_text}\n\n")
        if len(self.__responses) > 0:
            output += ("Лучший ответ:"
                       f"{sorted(self.__responses, key=lambda x: x.get_rating())}")
        else:
            output += "Пока нет ответов..."
        return output
