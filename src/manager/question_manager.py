import json
from pathlib import *

from src.model import question
from src.model.question import Question
from src.storage.question_encoder import QuestionEncoder


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

    def get_questions_for_user(self, userid: int):
        return [question for question in self.__questions if question.get_poster_id() == userid]

    def new_question(self, userid: int, username: str, text: str):
        self.__questions.append(Question(userid, username, text))

    def save(self, path: Path):
        ensure_file_exists(path)

        open(path, mode="w+").write(json.dumps(self.__questions, cls=QuestionEncoder))

    def read(self, path: Path):
        ensure_file_exists(path)

        raw = open(path, mode="r").read()
        loaded = json.loads(raw)
        if len(loaded) > 0:
            self.__questions = [question.parse(raw_question) for raw_question in loaded]

