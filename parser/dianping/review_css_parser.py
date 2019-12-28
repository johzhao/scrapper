import re

import requests


class ReviewCSSParser:
    font_id_pattern = re.compile(r'\.(\w+)?\s*{font-family:\s*\'(.+?)\';}')

    def __init__(self):
        self.cache = {}

    def get_position(self, url: str, tag: str, class_: str) -> (float, float):
        if url not in self.cache:
            content = self._get_resource(url)
            self._add_resource(url, content)

        mapping = self.cache[url]
        if tag not in mapping:
            raise Exception(f'The data tag {tag} was not exist in mapping {mapping}')

        if class_ not in mapping[tag]:
            raise Exception(f'The class {class_} was not exist in mapping {mapping[tag]}')

        position = mapping[tag][class_]

        return position['x'], position['y']

    @staticmethod
    def _get_resource(url: str) -> str:
        return requests.get(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'),
        }).text

    def _add_resource(self, url: str, content: str):
        # font_urls = {}
        # matches = self.font_id_pattern.findall(content)
        # for match in matches:
        #     font_id, font_name = match
        #     font_pattern = re.compile(rf'@font-face{{font-family: "{font_name}";src:url.*?;src:url.*?format.*?,url\("(.*?)"\)')
        #     font_match = font_pattern.findall(content)
        #     if len(font_match) != 1:
        #         raise Exception(f'Find font of {font_id} return {len(font_match)} results.')
        #
        #     font_urls[font_id] = f'http:{font_match[0]}'
        #
        # self.cache[url] = font_urls
        return NotImplemented
