import logging

from mongoengine import connect

import config
from export.export import export_shops_to_excel, export_reviews_to_excel
from model.shop_info import ShopInfo
from model.shop_review import ShopReview

log_format = ' %(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

from scheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)


def add_review_tasks(scheduler: Scheduler):
    connect(config.MONGO_DATABASE, host=config.MONGO_HOST, port=config.MONGO_PORT)
    for info in ShopInfo.objects:
        print(info)
        scheduler.append_url(f'https://www.dianping.com/shop/{info.id}/review_all?queryType=sortType&queryVal=latest',
                             'comment_first', f'https://www.dianping.com/shop/{info.id}')


def export():
    export_shops_to_excel('./output/shops.xls')
    export_reviews_to_excel('./output/reviews.xls')
    pass


def main():
    scheduler = Scheduler()
    # scheduler.append_url('https://www.dianping.com/search/keyword/2/0_%E4%B9%A6%E5%BA%97%E9%9F%B3%E5%83%8F', 'list', '')
    # add_review_tasks(scheduler)
    # scheduler.start()
    # scheduler.join()

    export()


if __name__ == '__main__':
    main()
