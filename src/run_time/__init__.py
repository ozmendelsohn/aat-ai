from abc import ABC, abstractmethod


class BaseCodeRunTime(ABC):
    """
    Abstract Base Code Runtime class for running code dynamically
    """
    @abstractmethod
    def run_code(self, code: str):
        pass
