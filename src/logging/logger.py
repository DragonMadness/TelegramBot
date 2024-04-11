from src.logging.log_level import *


class Logger:

    def __init__(self, output):
        self.__output = output

    def log(self, level: LogLevel, message: str):
        self.__output(level + message)

    def info(self, message: str):
        self.log(INFO, message)
