from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread, Event
import time

from src.util.formattable import Formattable


def create_callback_data(action: str, userid):
    return ";".join([action, str(userid)])


def parse_callback_data(raw: str) -> (str, int):
    split = raw.split(";")
    action = split[0]
    userid = int(split[1])
    return action, userid


class PagedMessageManager:

    def garbage_collector(self, event):
        while not event.is_set:
            if len(self.object_lists_cache) > 0:
                self.object_lists_cache.pop(0)
            time.sleep(1800)

    def __init__(self):
        self.object_lists_cache: dict[int: (list[Formattable], int)] = {}

        self.terminate_event = Event()
        self.gb = Thread(target=self.garbage_collector, args=(self.terminate_event,))
        self.gb.start()

    def destroy(self):
        self.terminate_event.set()
        self.gb.join()

    def save_entry_list(self, userid: int, entries: list[Formattable]):
        self.object_lists_cache[userid] = [entries, 0]

    def get_message(self, userid: int, entries: list[Formattable] = None) -> (str, InlineKeyboardMarkup):
        if entries is not None:
            self.save_entry_list(userid, entries)
        if userid not in self.object_lists_cache.keys():
            return None, None
        buttons = [[]]
        user_pages_data = self.object_lists_cache[userid]
        current = user_pages_data[1]
        if len(user_pages_data[0]) == 0:
            buttons[0].append(InlineKeyboardButton("Больше страниц нет...",
                                                   callback_data=create_callback_data("I", userid)))
        if current > 0:
            buttons[0].append(InlineKeyboardButton("Предыдущая страница",
                                                   callback_data=create_callback_data("PP", userid)))
        if current < len(user_pages_data[0]) - 1:
            buttons[0].append(InlineKeyboardButton("Следующая страница",
                                                   callback_data=create_callback_data("PN", userid)))
        return user_pages_data[0][current].get_string(), InlineKeyboardMarkup(buttons)

    def handle_callback(self, callback_data: str):
        action, userid = parse_callback_data(callback_data)
        if userid not in self.object_lists_cache.keys():
            return
        user_page_data = self.object_lists_cache[userid]
        current = user_page_data[1]
        if action == "I":
            return
        elif action == "PP" and current > 0:
            user_page_data[1] -= 1
        elif action == "PN" and current < (len(user_page_data[0]) - 1):
            user_page_data[1] += 1
