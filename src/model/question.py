from src.model import response
from src.util.formattable import Formattable
from src.model.user import User
from src.manager.user_manager import UserManager


def parse(raw: dict, user_manager: UserManager):
    return Question(user_manager.get_user(raw["userid"]),
                    raw["question_text"],
                    [response.parse(raw_response, user_manager) for raw_response in raw["responses"]])


class Question(Formattable):
    def __init__(self, author: User, question_text: str, responses: list[response.Response] = None):
        if responses is None:
            responses = []

        self.__author = author
        self.__question_text = question_text
        self.__responses: list[response.Response] = responses

    def get_author(self):
        return self.__author

    def get_text(self):
        return self.__question_text

    def get_responses(self):
        return self.__responses

    def add_response(self, author: User, text: str):
        self.__responses.append(response.Response(author, text))

    def get_string(self):
        output = (f"Вопрос пользователя @{self.__author.get_username()}.\n\n"
                  f"{self.__question_text}\n\n")
        if len(self.__responses) > 0:
            output += ("Лучший ответ:\n"
                       f"{sorted(self.__responses, key=lambda x: x.get_rating(), reverse=True)[0].get_string()}")
        else:
            output += "Пока нет ответов..."
        return output

    def serialize(self):
        return {"userid": self.__author.get_userid(),
                "question_text": self.__question_text,
                "responses": [response.serialize() for response in self.__responses]}
