def parse(raw: dict):
    return Response(raw["text"],
                    raw["rating"])


class Response:
    def __init__(self, response: str, rating: int = 0):
        self.__response = response
        self.__rating = rating

    def get_rating(self):
        return self.__rating

    def add_rating(self):
        self.__rating += 1

    def deduct_rating(self):
        self.__rating -= 1

    def serialize(self):
        return {"text": self.__response, "rating": self.__rating}
