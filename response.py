class Response:
    def __init__(self, response: str, rating: int = 0):
        self.__response = response
        self.__rating = rating

    def add_rating(self):
        self.__rating += 1

    def deduct_rating(self):
        self.__rating -= 1
