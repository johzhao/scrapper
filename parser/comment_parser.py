import logging
import re
from posixpath import normpath
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element

from model.shop_review import ShopReview
from parser.dianping.review_css_parser import ReviewCSSParser
from parser.dianping.svg_parser import SvgParser
from parser.parser import Parser

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CommentParser(Parser):
    css_pattern = re.compile(r'(//s3plus.meituan.net/v1/.+?/svgtextcss/.+?\.css)')
    shop_id_pattern = re.compile(r'.*/shop/(\d+)?/.*')
    page_id_pattern = re.compile(r'.*/shop/\d+?/review_all/p(\d+?)')
    rating_pattern = re.compile(r'sml-str(\d+)')
    timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')
    css_parser = ReviewCSSParser()
    svg_parser = SvgParser()

    def __init__(self, delegate):
        super().__init__(delegate)

    def parse(self, url: str, content: str):
        html = etree.HTML(content, etree.HTMLParser())
        parse_next_page = True
        elements = html.xpath('//div[@class="reviews-items"]/ul/li')
        if len(elements) == 0:
            raise Exception(f'Failed to parse comments from {content}')

        css_url = self._parse_css(content)

        index = 1
        for element in elements:
            timestamp = self._parse_timestamp(element)
            if not (timestamp.startswith('2019') or timestamp.startswith('2020')):
                parse_next_page = False
                continue

            shop_review = ShopReview()
            shop_review.id = self._parse_comment_id(url, index)
            shop_review.username = self._parse_username(element)
            shop_review.shop_id = self._parse_shop_id(url)
            shop_review.shop_name = self._parse_shop_name(element)
            shop_review.rating = self._parse_rating(element)
            shop_review.comment = self._parse_comment(css_url, element)
            shop_review.timestamp = timestamp

            self.delegate.save_content(shop_review, 'comment')
            index += 1

        if parse_next_page:
            elements = html.xpath('//a[@class="NextPage"]/@href')
            if elements:
                comment_url = urljoin(url, elements[0])
                url_components = urlparse(comment_url)
                path = normpath(url_components.path)
                comment_url = urlunparse((url_components.scheme, url_components.netloc, path, url_components.params,
                                          url_components.query, url_components.fragment))
                self.delegate.append_url(comment_url, 'comment', url)

    def _parse_css(self, content: str) -> str:
        css_matchs = self.css_pattern.findall(content)
        if len(css_matchs) != 1:
            raise Exception(f'Find {len(css_matchs)} css in the content')

        return f'http:{css_matchs[0]}'

    def _parse_comment_id(self, url: str, comment_id: int) -> str:
        matches = self.shop_id_pattern.findall(url)
        if len(matches) != 1:
            raise Exception(f'Failed to parse shop id from {url}')
        shop_id = matches[0].strip()

        matches = self.page_id_pattern.findall(url)
        if not matches:
            page_id = 1
        else:
            page_id = matches[0].strip()

        return f'{shop_id}-{page_id}-{comment_id}'

    @staticmethod
    def _parse_username(html: _Element) -> str:
        element = html.xpath('div[@class="main-review"]/div[@class="dper-info"]/a/text()')[0]
        return element.strip()

    def _parse_shop_id(self, url: str) -> str:
        matches = self.shop_id_pattern.findall(url)
        if len(matches) != 1:
            raise Exception(f'Failed to parse shop id from {url}')
        return matches[0].strip()

    @staticmethod
    def _parse_shop_name(html: _Element) -> str:
        elements = html.xpath(('div[@class="main-review"]/div[contains(@class, "misc-info")]/'
                               'span[@class="shop"]/text()'))
        return elements[0].strip()

    def _parse_rating(self, html: _Element) -> float:
        elements = html.xpath(('div[@class="main-review"]/div[contains(@class, "review-rank")]/'
                               'span[1]/@class'))
        tags = elements[0].split()
        rating = 0.0
        for tag in tags:
            matches = self.rating_pattern.findall(tag)
            if not matches:
                continue
            rating = int(matches[0]) / 10.0
            break

        return rating

    def _parse_comment(self, css_url: str, html: _Element) -> str:
        elements = html.xpath('div[@class="main-review"]/div[contains(@class, "review-words")]')
        element = elements[0]

        comment = []
        if element.text is not None:
            comment.append(element.text.strip())

        for child in element.getchildren():
            if child.tag == 'div':
                break

            if child.tag == 'img':
                # 图片的text也为None,但tail可能有文字
                pass
            elif child.text is None:
                svg_url, x, y = self.css_parser.get_position(css_url, child.tag, child.attrib['class'])
                self.svg_parser.append_svg(svg_url)
                text = self.svg_parser.parse(svg_url, x, y)
                comment.append(text)

            if child.tail is not None:
                comment.append(child.tail.strip())

        return ''.join(comment)

    def _parse_timestamp(self, html: _Element) -> str:
        elements = html.xpath(('div[@class="main-review"]/div[contains(@class, "misc-info")]/'
                               'span[@class="time"]/text()'))
        text = elements[0].strip()
        matches = self.timestamp_pattern.findall(text)
        if not matches:
            raise Exception(f'Failed to find timestamp in {text}')
        return matches[0].strip()
