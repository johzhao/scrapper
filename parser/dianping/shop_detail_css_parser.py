import re

import requests


class ShopDetailCSSParser:
    font_id_pattern = re.compile(r'\.(\w+)?\s*{font-family:\s*\'(.+?)\';}')

    def __init__(self):
        self.cache = {}

    def get_font_url_by_type(self, url: str, type_: str) -> str:
        if url not in self.cache:
            content = self._get_resource(url)
            self._add_resource(url, content)

        mapping = self.cache[url]
        if type_ not in mapping:
            raise Exception(f'The data type {type_} was not exist in mapping {mapping}')

        return mapping[type_]

    @staticmethod
    def _get_resource(url: str) -> str:
        return requests.get(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'),
        }).text

    def _add_resource(self, url: str, content: str):
        font_urls = {}
        matches = self.font_id_pattern.findall(content)
        for match in matches:
            font_id, font_name = match
            font_pattern = re.compile(rf'@font-face{{font-family: "{font_name}";src:url.*?;src:url.*?format.*?,url\("(.*?)"\)')
            font_match = font_pattern.findall(content)
            if len(font_match) != 1:
                raise Exception(f'Find font of {font_id} return {len(font_match)} results.')

            font_urls[font_id] = f'http:{font_match[0]}'

        self.cache[url] = font_urls


def test_shop_detail_css_parser():
    with open('./shop_detail.css', 'r') as ifile:
        data = ifile.read()

    parser = ShopDetailCSSParser()
    css_url = ('http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/'
               'shop_detail.css')

    parser._add_resource(css_url, data)

    print(f'url for font address was {parser.get_font_url_by_type(css_url, "address")}')
    print(f'url for font num was {parser.get_font_url_by_type(css_url, "num")}')
