from src.util.formattable import Formattable
from src.util import messages
from src.model.user import User
from src.manager.user_manager import UserManager


def parse(raw: dict, user_manager: UserManager):
    return Response(user_manager.get_user(raw["author_id"]),
                    raw["text"],
                    raw["rating"])


class Response(Formattable):
    def __init__(self, author: User, text: str, rating: int = 0):
        self.__author = author
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
                .replace("%response_author%", str(self.__author.get_username()))
                .replace("%rating_sign%", sign)
                .replace("%rating%", str(self.__rating))
                .replace("%response_text%", self.__text))

    def serialize(self):
        return {"author_id": self.__author.get_userid(),
                "text": self.__text,
                "rating": self.__rating}
