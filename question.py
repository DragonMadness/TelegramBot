import response


def parse(raw: dict):
    return Question(int(raw["poster_id"]),
                    raw["poster_name"],
                    raw["question_text"],
                    [response.parse(raw_response) for raw_response in raw["responses"]])


class Question:
    def __init__(self, poster_id: int, poster_name: str, question_text: str, responses: list[response.Response] = ()):
        self.__poster_id = poster_id
        self.__poster_name = poster_name
        self.__question_text = question_text
        self.__responses: list[response.Response] = responses

    def get_poster_id(self):
        return self.__poster_id

    def get_poster_name(self):
        return self.__poster_name

    def get_text(self):
        return self.__question_text

    def get_responses(self):
        return self.__responses

    def get_formatted(self):
        output = (f"Вопрос пользователя @{self.__poster_name}.\n\n"
                  f"{self.__question_text}\n\n")
        if len(self.__responses) > 0:
            output += ("Лучший ответ:"
                       f"{sorted(self.__responses, key=lambda x: x.get_rating())}")
        else:
            output += "Пока нет ответов..."
        return output

    def serialize(self):
        return {"poster_id": self.__poster_id,
                "poster_name": self.__poster_name,
                "question_text": self.__question_text,
                "responses": [response.serialize() for response in self.__responses]}
