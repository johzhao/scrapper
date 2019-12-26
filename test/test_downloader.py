import logging

import config
from downloader.downloader import Downloader

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_downloader():
    downloader = Downloader(config.HEADERS)
    result = downloader.download_url('https://www.dianping.com/shop/90556783/review_all',
                                     'https://www.dianping.com/shop/90556783')
    logger.info(result)
