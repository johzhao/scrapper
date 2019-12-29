import logging

from mongoengine import Document
from mongoengine import connect

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Storage:

    def __init__(self, database: str, host: str, port: int):
        connect(database, host=host, port=port)

    def save_content(self, content: Document, type_: str):
        logger.info(f'Save type {type_}, content {content}')
        content.save()


def test_storage():
    import config
    from model.shop_info import ShopInfo
    storage = Storage(config.MONGO_DATABASE, config.MONGO_HOST, config.MONGO_PORT)

    shop_info = ShopInfo()
    shop_info.id = 1
    shop_info.name = 'Test'
    shop_info.address = 'Address'
    shop_info.phone_number = '022-12345678'
    shop_info.url = 'http://dianping.com/12345678'
    shop_info.rating = '5 Starts'
    shop_info.reviews = 1234
    shop_info.avg_cost = 10.1
    shop_info.production_rating = 4.5
    shop_info.environment_rating = 5.6
    shop_info.service_rating = 6.7

    storage.save_content(shop_info, 'detail')
