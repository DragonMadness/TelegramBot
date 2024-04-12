import json
from pathlib import *

from src.model.question import *
from src.model.user import User


def ensure_file_exists(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

    raw = open(path, mode="r+")
    if len(raw.read()) == 0:
        raw.write("[]")


class QuestionManager:
    def __init__(self, questions: list[Question] = None):
        if questions is None:
            questions = []
        self.__questions = questions

    def get_questions(self):
        return self.__questions

    def get_questions_for_user(self, user: User):
        return [question for question in self.__questions if question.get_author() == user]

    def new_question(self, user: User, text: str):
        self.__questions.append(Question(user, text))

    def save(self, path: Path):
        ensure_file_exists(path)

        with open(path, mode="w+") as file:
            file.write(json.dumps([question.serialize() for question in self.__questions]))

    def read(self, path: Path, user_manager: UserManager):
        ensure_file_exists(path)

        with open(path, mode="r") as file:
            raw = file.read()
            loaded = json.loads(raw)
            if len(loaded) > 0:
                self.__questions = [parse(raw_question, user_manager) for raw_question in loaded]
