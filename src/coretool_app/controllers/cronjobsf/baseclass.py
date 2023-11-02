from abc import ABC, abstractmethod


class abstractstatic(staticmethod):
    __slots__ = ()
    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True


class Crontab(ABC):
    @abstractstatic
    def start(self, *args, **kwargs):
        pass
