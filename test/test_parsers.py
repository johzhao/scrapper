import logging

from parser.list_parser import ListParser

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MockParserDelegate:

    def save_content(self, content: dict, type_: str):
        logger.info(f'Save type {type_}, content {content}')
        pass

    def append_url(self, url: str, type_: str, reference: str):
        # logger.info(f'Append url {url}, type {type_}, reference {reference}')
        pass


def test_list_parser():
    with open('./test_files/shop_list.html', 'r') as html_file:
        data = html_file.read()
    parser = ListParser(MockParserDelegate())
    parser.parse('https://www.dianping.com/search/keyword/2/0_%E4%B9%A6%E5%BA%97%E9%9F%B3%E5%83%8F', data)
    pass
