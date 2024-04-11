import abc
from abc import abstractmethod


class Formattable(abc.ABC):

    @abstractmethod
    def get_string(self):
        pass
