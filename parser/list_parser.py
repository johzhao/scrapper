import logging
import re

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element

# from parser.dianping.font_parser import FontParser
from parser.dianping.shop_detail_css_parser import ShopDetailCSSParser
from parser.parser import Parser

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ListParser(Parser):
    # font_parser = FontParser('./test_files/basefont.woff', './test_files/basefont.json')
    css_parser = ShopDetailCSSParser()
    css_pattern = re.compile(r'(//s3plus.meituan.net/v1/.+?/svgtextcss/.+?\.css)')

    def __init__(self, delegate):
        super().__init__(delegate)

    def parse(self, url: str, content: str):
        html = etree.HTML(content, etree.HTMLParser())

        # 获取每个店铺条目
        result = html.xpath('//ul/li/div[@class="txt"]')
        if len(result) == 0:
            raise Exception(f'Failed to parse shop link from list url {url}')

        # css_url = self._parse_css(content)
        # num_font_url = self.css_parser.get_font_url_by_type(css_url, 'shopNum')
        # self.font_parser.append_font(num_font_url)

        shops = []
        for item in result:
            shop_name = item.xpath('div[@class="tit"]/a/@title')[0]
            shop_url = item.xpath('div[@class="tit"]/a/@href')[0]
            logger.info(f'Got one shop {shop_name} with url {shop_url}')

            # 解析评论数量，剔除评论数少于10条的店铺
            elements = item.xpath('div[@class="comment"]/a[@class="review-num"]//b')
            if elements:
                element = elements[0]
                review_count = self._parse_review_count(element, 'num_font_url')
                if review_count > 10:
                    shops.append(shop_url)
                else:
                    logger.info(f'The comments of the shop {shop_name} was less than 10. Ignore it.')

        # 获取下一页的链接
        if shops:
            result = html.xpath('//div[@class="page"]/a[@class="next"]/@href')
            for item in result:
                self.delegate.append_url(item, 'list', url)

        for shop in shops:
            self.delegate.append_url(shop, 'detail', url)

    def _parse_css(self, content: str) -> str:
        css_matchs = self.css_pattern.findall(content)
        if len(css_matchs) != 1:
            raise Exception(f'Find {len(css_matchs)} css in the content')

        return f'http:{css_matchs[0]}'

    def _parse_review_count(self, html: _Element, num_font_url: str) -> int:
        content = self._parse_number(html, num_font_url)
        return int(content)

    @staticmethod
    def _parse_number(element: _Element, _: str) -> str:
        result = []
        if element.text is not None:
            result.append(element.text.strip())

        for child in element.iterchildren():
            if child.attrib['class'] == 'shopNum':
                # result.append(self.font_parser.parse(num_font_url, child.text).strip())
                result.append('1')
            else:
                result.append(child.text.strip())

            if child.tail is not None:
                result.append(child.tail.strip())

        return ''.join(result).strip()
