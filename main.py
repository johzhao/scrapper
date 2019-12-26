import logging
logging.basicConfig(level=logging.INFO)

from scheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)


def main():
    scheduler = Scheduler()
    scheduler.append_url('https://www.dianping.com/search/keyword/2/0_%E4%B9%A6%E5%BA%97%E9%9F%B3%E5%83%8F', 'list', '')
    scheduler.start()
    scheduler.join()


if __name__ == '__main__':
    main()
