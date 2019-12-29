import re

import requests


class ReviewCSSParser:
    svg_id_pattern = re.compile(r'(\w*?)\[class\^="(\w*?)"\].*?background-image:\s*url\((.*?)\);')
    class_pattern = re.compile(r'\.(\w*?){background:([.\d-]+?)px ([.\d-]+?)px;}')

    def __init__(self):
        self.cache = {}

    def get_position(self, url: str, tag: str, class_: str) -> (str, float, float):
        if url not in self.cache:
            content = self._get_resource(url)
            self._add_resource(url, content)

        mapping = self.cache[url]
        if tag not in mapping:
            raise Exception(f'The data tag {tag} was not exist in mapping {mapping}')

        if class_ not in mapping[tag]:
            raise Exception(f'The class {class_} was not exist in mapping {mapping[tag]}')

        position = mapping[tag][class_]

        return mapping[tag]['svg_url'], position['x'], position['y']

    @staticmethod
    def _get_resource(url: str) -> str:
        return requests.get(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'),
        }).text

    def _add_resource(self, url: str, content: str):
        matches = self.svg_id_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find svg in css')

        prefixes = {}
        mapping = {}
        for item in matches:
            mapping[item[0]] = {
                'svg_url': f'http:{item[2]}',
            }
            prefixes[item[1]] = item[0]

        matches = self.class_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find class in css')

        for item in matches:
            for prefix, key in prefixes.items():
                if item[0].startswith(prefix):
                    # noinspection PyTypeChecker
                    mapping[key][item[0]] = {
                        'x': -float(item[1]),
                        'y': -float(item[2]),
                    }
                    break

        self.cache[url] = mapping


def test_review_css_parser():
    parser = ReviewCSSParser()
    with open('../../test_files/29b5d13bd29b2ddf770815051787caf1.css', 'r') as ifile:
        data = ifile.read()
    parser._add_resource('29b5d13bd29b2ddf770815051787caf1.css', data)
    svg_url, x, y = parser.get_position('29b5d13bd29b2ddf770815051787caf1.css', 'svgmtsi', 'wbepe')
    print(f'svg_url: {svg_url}, x = {x}, y = {y}')
