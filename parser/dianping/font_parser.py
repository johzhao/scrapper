import json
import logging
from io import BytesIO

import requests
# noinspection PyPackageRequirements
from fontTools.ttLib import TTFont

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class FontParser:
    base_glyph_mapping = {}
    base_str_mapping = {}
    font_mapping = {}

    def __init__(self, base_font_file: str, base_font_mapping_file: str):
        self._create_base_mapping(base_font_file, base_font_mapping_file)

    def append_font(self, url: str) -> None:
        if url in self.font_mapping:
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
            for base_key, basse_glyph in self.base_glyph_mapping.items():
                if glyph == basse_glyph:
                    font_str_mapping[base_key] = self.base_str_mapping[base_key]

        self.font_mapping[url] = font_str_mapping

    def parse(self, url: str, code: str) -> str:
        if url not in self.font_mapping:
            raise Exception(f'Failed to find {url} font mapping')

        mapping = self.font_mapping[url]
        if code in mapping:
            return mapping[code]
        else:
            logger.warning(f'Failed to find the character for code {code}')
            return code

    def _create_base_mapping(self, base_font_file: str, base_font_mapping_file: str) -> None:
        font = TTFont(base_font_file)
        uni_list = font.getGlyphNames()
        logger.info(f'There is {len(uni_list)} fonts in {base_font_file}')

        with open(base_font_mapping_file, 'r') as ifile:
            mapping = json.load(ifile)

        for key, value in mapping.items():
            glyph = font['glyf'][key]
            key = eval(r"u'\u" + key[3:] + "'")
            self.base_glyph_mapping[key] = glyph
            self.base_str_mapping[key] = value
