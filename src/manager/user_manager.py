from pathlib import Path
import json
from src.model.user import *


def ensure_file_exists(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

    raw = open(path, mode="r+")
    if len(raw.read()) == 0:
        raw.write("[]")


class UserManager:
    def __init__(self):
        self.__users: list[User] = []

    def compute_if_not_exists(self, userid: int, username: str):
        user = self.get_user(userid)
        if user is None:
            user = self.new_user(userid, username)
        return user

    def new_user(self, userid: int, username: str):
        user = User(userid, username)
        self.__users.append(user)
        return user

    def get_user(self, userid: int):
        for user in self.__users:
            if user.get_userid() == userid:
                return user
        return None

    def get_notifiable_users(self):
        return [user for user in self.__users if user.do_notify_new_questions()]

    def save(self, path: Path):
        ensure_file_exists(path)

        with open(path, mode="w+") as file:
            file.write(json.dumps([user.serialize() for user in self.__users]))

    def read(self, path: Path):
        ensure_file_exists(path)

        with open(path, mode="r") as file:
            raw = file.read()
            loaded = json.loads(raw)
            if len(loaded) > 0:
                self.__users = [parse(raw_question) for raw_question in loaded]
