import logging
import re

import requests

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# {
#     "bb.svg": {
#         "font-size": 14,
#         "data": [
#             {
#                 "height": 40,
#                 "content": []
#             },
#             {
#                 "height": 88,
#                 "content": []
#             },
#             {
#                 "height": 138,
#                 "content": []
#             }
#         ]
#     }
# }

class SvgParser:
    font_size_pattern = re.compile(r'font-size:(\d+?)px')
    main_svg_identify_pattern = re.compile(r'<textPath xlink:')
    num_svg_identify_pattern = re.compile(r'<text x="[\d ]+" y="\d+">')
    supplyment_svg_identify_pattern = re.compile(r'<text x="\d+" y="\d+">')

    main_height_pattern = re.compile(r'<path id="(\d+?)" d="M\d+? (\d+?) H\d+?"/>')
    main_text_pattern = re.compile(r'<textPath xlink:href="#(\d+?)" textLength="\d+?">(.+?)</textPath>')
    num_pattern = re.compile(r'<text x="[\d ]+?" y="(\d+?)">(.*?)</text>')
    supplyment_pattern = re.compile(r'<text x="\d+?" y="(\d+)?">(.*?)</text>')

    def __init__(self):
        self.svg_mapping = {}

    def append_svg(self, url: str) -> None:
        if url in self.svg_mapping:
            return

        response = requests.get(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'),
        })
        self._parse_svg(url, response.text)

    def parse(self, url: str, x: float, y: float) -> str:
        if url not in self.svg_mapping:
            raise Exception(f'Failed to find svg for {url}')
        font_size = self.svg_mapping[url]['font-size']
        for item in self.svg_mapping[url]['data']:
            if item['height'] >= y:
                x_offset = int(x // font_size)
                return item['content'][x_offset]

        raise Exception(f'Failed to find text for svg {url}, x {x}, y {y}')

    def _parse_svg(self, url: str, content: str):
        matches = self.font_size_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find font size in svg {url}')
        font_size = int(matches[0])

        matches = self.main_svg_identify_pattern.findall(content)
        if matches:
            result = self._parse_main_svg(url, font_size, content)
            self.svg_mapping[url] = result
            return

        matches = self.supplyment_svg_identify_pattern.findall(content)
        if matches:
            result = self._parse_supplement_svg(url, font_size, content)
            self.svg_mapping[url] = result
            return

        matches = self.num_svg_identify_pattern.findall(content)
        if matches:
            result = self._parse_num_svg(url, font_size, content)
            self.svg_mapping[url] = result
            return

        raise Exception(f'Failed to verify the svg format of {url}')

    def _parse_main_svg(self, url: str, font_size: int, content: str) -> dict:
        logger.info(f'Parse the num svg from {url} with font size {font_size}')
        matches = self.main_height_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find height from the main svg {url}')
        heights = {}
        for item in matches:
            heights[item[0]] = int(item[1])

        matches = self.main_text_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find text from the main svg {url}')

        result = {
            'font-size': font_size,
            'data': []
        }
        for item in matches:
            result['data'].append({
                'height': heights[item[0]],
                'content': item[1]
            })
        return result

    def _parse_num_svg(self, url: str, font_size: int, content: str) -> dict:
        logger.info(f'Parse the num svg from {url} with font size {font_size}')
        matches = self.num_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find content from the num svg {url}')

        result = {
            'font-size': font_size,
            'data': []
        }
        for item in matches:
            result['data'].append({
                'height': int(item[0]),
                'content': item[1],
            })
        return result

    def _parse_supplement_svg(self, url: str, font_size: int, content: str) -> dict:
        logger.info(f'Parse the supplement svg from {url} with font size {font_size}')
        matches = self.supplyment_pattern.findall(content)
        if not matches:
            raise Exception(f'Failed to find content from the supplement svg {url}')

        result = {
            'font-size': font_size,
            'data': []
        }
        for item in matches:
            result['data'].append({
                'height': int(item[0]),
                'content': item[1],
            })
        return result


def test_parse_main_svg():
    parser = SvgParser()
    url = '../../test_files/svgmtsi.svg'
    with open(url, 'r') as ifile:
        data = ifile.read()
    parser._parse_svg(url, data)
    print(parser)


def test_parse_num_svg():
    parser = SvgParser()
    url = '../../test_files/cc.svg'
    with open(url, 'r') as ifile:
        data = ifile.read()
    parser._parse_svg(url, data)
    print(parser)


def test_parse_supplement_svg():
    parser = SvgParser()
    url = '../../test_files/bb.svg'
    with open(url, 'r') as ifile:
        data = ifile.read()
    parser._parse_svg(url, data)
    print(parser)
