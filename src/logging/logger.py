from src.logging.log_level import LogLevel


class Logger:

    def __init__(self, output):
        self.__output = output

    def log(self, level: LogLevel, message: str):
        self.__output(level + message)


