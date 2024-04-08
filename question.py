from response import Response


class Question:
    def __init__(self, question_text: str, responses: list[Response] = ()):
        self.__question_text = question_text
        self.__responses = responses
