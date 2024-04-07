class LogLevel(str):
    def __init__(self, prefix: str):
        self.__prefix = prefix

    def __add__(self, other):
        return self.__prefix + other


INFO = LogLevel("[INFO] ")
WARN = LogLevel("[WARN] ")
ERR = LogLevel("[ERR] ")
