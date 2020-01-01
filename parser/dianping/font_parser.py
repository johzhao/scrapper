import json
import logging
from collections import defaultdict
from io import BytesIO

import requests
# noinspection PyPackageRequirements
from fontTools.ttLib import TTFont

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class FontParser:
    base_glyph_mapping = defaultdict(dict)
    base_str_mapping = defaultdict(dict)
    font_mapping = {}

    def __init__(self):
        pass

    def setup_base_font_mapping(self, base_font_file: str, base_font_mapping_file: str, type_: str):
        if type_ in self.base_str_mapping:
            return
        self._create_base_mapping(base_font_file, base_font_mapping_file, type_)

    def append_font(self, type_: str, url: str) -> None:
        if type_ not in self.font_mapping:
            self.font_mapping[type_] = {}

        if url in self.font_mapping[type_]:
            return

        response = requests.get(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'),
        })
        font_file = BytesIO(response.content)
        font = TTFont(font_file)
        uni_list = font.getGlyphNames()
        font_str_mapping = {}
        for key in uni_list:
            glyph = font['glyf'][key]
            for base_key, basse_glyph in self.base_glyph_mapping[type_].items():
                if glyph == basse_glyph:
                    font_str_mapping[base_key] = self.base_str_mapping[type_][base_key]

        self.font_mapping[type_][url] = font_str_mapping

    def parse(self, type_: str, url: str, code: str) -> str:
        if type_ not in self.font_mapping:
            raise Exception(f'Failed to find type {type_} in font mapping')

        if url not in self.font_mapping[type_]:
            raise Exception(f'Failed to find {url} in {type_} font mapping')

        mapping = self.font_mapping[type_][url]
        if code in mapping:
            return mapping[code]
        else:
            logger.warning(f'Failed to find the character for code {code}')
            return code

    def _create_base_mapping(self, base_font_file: str, base_font_mapping_file: str, type_: str) -> None:
        font = TTFont(base_font_file)
        uni_list = font.getGlyphNames()
        logger.info(f'There is {len(uni_list)} fonts in {base_font_file}')

        with open(base_font_mapping_file, 'r') as ifile:
            mapping = json.load(ifile)

        for key, value in mapping.items():
            glyph = font['glyf'][key]
            key = eval(r"u'\u" + key[3:] + "'")
            self.base_glyph_mapping[type_][key] = glyph
            self.base_str_mapping[type_][key] = value
