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
from parser.parser import Parser

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CommentParser(Parser):
    css_pattern = re.compile(r'(//s3plus.meituan.net/v1/.+?/svgtextcss/.+?\.css)')
    shop_id_pattern = re.compile(r'.*/shop/(\d+)?/.*')
    rating_pattern = re.compile(r'sml-str(\d+)')
    timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')

    def __init__(self, delegate):
        super().__init__(delegate)

    def parse(self, url: str, content: str):
        html = etree.HTML(content, etree.HTMLParser())
        parse_next_page = True
        elements = html.xpath('//div[@class="reviews-items"]/ul/li')
        if len(elements) == 0:
            raise Exception(f'Failed to parse comments from {content}')

        css_url = self._parse_css(content)
        print(css_url)

        for element in elements:
            timestamp = self._parse_timestamp(element)
            if not timestamp.startswith('2019'):
                parse_next_page = False
                continue

            shop_review = ShopReview()
            shop_review.username = self._parse_username(element)
            shop_review.shop_id = self._parse_shop_id(url)
            shop_review.shop_name = self._parse_shop_name(element)
            shop_review.rating = self._parse_rating(element)
            shop_review.comment = self._parse_comment(element)
            shop_review.timestamp = timestamp

            self.delegate.save_content(shop_review, 'comment')

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

    def _parse_comment(self, html: _Element) -> str:
        elements = html.xpath('div[@class="main-review"]/div[contains(@class, "review-words")]')
        return NotImplemented

    def _parse_timestamp(self, html: _Element) -> str:
        elements = html.xpath(('div[@class="main-review"]/div[contains(@class, "misc-info")]/'
                               'span[@class="time"]/text()'))
        text = elements[0].strip()
        matches = self.timestamp_pattern.findall(text)
        if not matches:
            raise Exception(f'Failed to find timestamp in {text}')
        return matches[0].strip()
