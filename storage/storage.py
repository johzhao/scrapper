import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Storage:

    def __init__(self):
        pass

    def save_content(self, content: dict, type_: str):
        logger.info(f'Save type {type_}, content {content}')
