from src.util.formattable import Formattable
from src.util import messages


def parse(raw: dict):
    return Response(raw["author"],
                    raw["author_name"],
                    raw["text"],
                    raw["rating"])


class Response(Formattable):
    def __init__(self, author: int, author_name: str, text: str, rating: int = 0):
        self.__author = author
        self.__author_name = author_name
        self.__text = text
        self.__rating = rating

    def get_rating(self):
        return self.__rating

    def get_author(self):
        return self.__author

    def add_rating(self):
        self.__rating += 1

    def deduct_rating(self):
        self.__rating -= 1

    def get_string(self):
        sign = "⛔"
        if self.__rating > 0:
            sign = "⬆"
        elif self.__rating < 0:
            sign = "⬇"
        return (messages.response_view_format
                .replace("%response_author%", str(self.__author_name))
                .replace("%rating_sign%", sign)
                .replace("%rating%", str(self.__rating))
                .replace("%response_text%", self.__text))

    def serialize(self):
        return {"author": self.__author, "author_name": self.__author_name, "text": self.__text, "rating": self.__rating}
