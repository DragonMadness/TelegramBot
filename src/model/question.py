from src.model import response
from src.util.formattable import Formattable


def parse(raw: dict):
    return Question(int(raw["poster_id"]),
                    raw["poster_name"],
                    raw["question_text"],
                    [response.parse(raw_response) for raw_response in raw["responses"]])


class Question(Formattable):
    def __init__(self, poster_id: int, poster_name: str, question_text: str, responses: list[response.Response] = None):
        if responses is None:
            responses = []

        self.__author_id = poster_id
        self.__author_name = poster_name
        self.__question_text = question_text
        self.__responses: list[response.Response] = responses

    def get_author_id(self):
        return self.__author_id

    def get_author_name(self):
        return self.__author_name

    def get_text(self):
        return self.__question_text

    def get_responses(self):
        return self.__responses

    def add_response(self, author: int, author_name: str, text: str):
        self.__responses.append(response.Response(author, author_name, text))

    def get_string(self):
        output = (f"Вопрос пользователя @{self.__author_name}.\n\n"
                  f"{self.__question_text}\n\n")
        if len(self.__responses) > 0:
            output += ("Лучший ответ:\n"
                       f"{sorted(self.__responses, key=lambda x: x.get_rating(), reverse=True)[0].get_string()}")
        else:
            output += "Пока нет ответов..."
        return output

    def serialize(self):
        return {"poster_id": self.__author_id,
                "poster_name": self.__author_name,
                "question_text": self.__question_text,
                "responses": [response.serialize() for response in self.__responses]}
