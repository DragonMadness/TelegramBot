from src.util.formattable import Formattable


def parse(raw: dict):
    return Response(raw["text"],
                    raw["rating"])


class Response(Formattable):
    def __init__(self, author: int, response: str, rating: int = 0):
        self.__author = author
        self.__response = response
        self.__rating = rating

    def get_rating(self):
        return self.__rating

    def add_rating(self):
        self.__rating += 1

    def deduct_rating(self):
        self.__rating -= 1

    def get_string(self):
        return self.serialize()  # TODO make a better repr

    def serialize(self):
        return {"text": self.__response, "rating": self.__rating}
