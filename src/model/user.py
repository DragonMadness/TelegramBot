def parse(raw: dict):
    return User(raw["userid"],
                raw["username"],
                raw["notify_new_questions"],
                raw["notify_new_answers"])


class User:
    def __init__(self, userid: int, username: str, notify_new_questions: bool = False, notify_new_answers: bool = True):
        self.__userid = userid
        self.__username = username
        self.__notify_new_questions = notify_new_questions
        self.__notify_new_answers = notify_new_answers

    def get_userid(self):
        return self.__userid

    def get_username(self):
        return self.__username

    def do_notify_new_questions(self):
        return self.__notify_new_questions

    def do_notify_new_answers(self):
        return self.__notify_new_answers

    def set_notify_new_questions(self, notify_new_questions: bool):
        self.__notify_new_questions = notify_new_questions

    def set_notify_new_answers(self, notify_new_answers: bool):
        self.__notify_new_answers = notify_new_answers

    def serialize(self):
        return {"userid": self.__userid,
                "username": self.__username,
                "notify_new_questions": self.__notify_new_questions,
                "notify_new_answers": self.__notify_new_answers}
