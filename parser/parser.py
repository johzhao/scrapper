import abc


class Parser(abc.ABC):

    def __init__(self, delegate):
        self.delegate = delegate

    @abc.abstractmethod
    def parse(self, url: str, content: str):
        return NotImplemented
