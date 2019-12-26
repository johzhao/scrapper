import logging

from lxml import etree

from parser.parser import Parser

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ListParser(Parser):

    def __init__(self, delegate):
        super().__init__(delegate)

    def parse(self, url: str, content: str):
        html = etree.HTML(content, etree.HTMLParser())

        # 获取每个店铺条目
        result = html.xpath('//ul/li//div[@class="txt"]')
        if len(result) == 0:
            raise Exception(f'Failed to parse shop link from list url {url}')

        for item in result:
            shop_name = item.xpath('div[@class="tit"]/a/@title')[0]
            shop_url = item.xpath('div[@class="tit"]/a/@href')[0]
            logger.info(f'Got one shop {shop_name} with url {shop_url}')

            # 解析评论数量，剔除评论数少于10条的店铺
            element = item.xpath('div[@class="comment"]/a[@class="review-num"]')
            comments = element[0].xpath('b/svgmtsi | b/text()')
            if len(comments) >= 2:
                self.delegate.append_url(item, 'detail', url)
            else:
                logger.info(f'The comments of the shop {shop_name} was less than 10. Ignore it.')

        # 获取下一页的链接
        result = html.xpath('//div[@class="page"]/a[@class="next"]/@href')
        for item in result:
            self.delegate.append_url(item, 'list', url)
