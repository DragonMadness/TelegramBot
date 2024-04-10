from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread, Event
import time

entries_map = []


def garbage_collector(event):
    while not event.is_set:
        if len(entries_map) > 0:
            entries_map.pop(0)
        time.sleep(1800)


terminate_event = Event()
gb = Thread(target=garbage_collector, args=(terminate_event,))
gb.start()


def destroy():
    terminate_event.set()
    gb.join()


def create_callback_data(action: str, page: int, entries_id: int):
    return ";".join([action, str(page), str(entries_id)])


def parse_callback_data(raw: str):
    split = raw.split(";")
    action = split[0]
    page = int(split[1])
    entries = entries_map[int(split[2])]
    return action, page, entries


def save_entry_list(entries: list[str]):
    index = len(entries_map)
    entries_map.append(entries)
    return index


def get_message(entries: list[str], page: int) -> (str, InlineKeyboardMarkup):
    buttons = [[]]
    if page > 0:
        buttons[0].append(InlineKeyboardButton("Предыдущая страница",
                                               callback_data=create_callback_data("P", page,
                                                                                  save_entry_list(entries))))
    if page < len(entries) - 1:
        buttons[0].append(InlineKeyboardButton("Следующая страница",
                                               callback_data=create_callback_data("N", page,
                                                                                  save_entry_list(entries))))
    return entries[page], InlineKeyboardMarkup(buttons)


def handle_callback(callback_data: str):
    action, page, entries = parse_callback_data(callback_data)
    if action == "P" and page > 0:
        page -= 1
    elif action == "N" and page < (len(entries) - 1):
        page += 1
    return entries, page
