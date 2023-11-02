from abc import abstractmethod
from abc import ABCMeta


class ApiRestAbstractController(metaclass=ABCMeta):
    @abstractmethod
    def get_data(self, **kwargs):
        pass
