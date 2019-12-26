from parser.parser import Parser


class CommentParser(Parser):

    def __init__(self, delegate):
        super().__init__(delegate)
        pass

    def parse(self, url: str, content: str):
        pass
