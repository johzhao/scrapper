import logging
import random
import threading
import time
from typing import Optional

from mongoengine import Document

import config
from downloader.downloader import Downloader
from model.task import Task
from parser.comment_parser import CommentParser
from parser.detail_parser import DetailParser
from parser.list_parser import ListParser
from scheduler.task_queue import TaskQueue
from storage.storage import Storage

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Scheduler(threading.Thread):

    def __init__(self):
        super().__init__()
        self.parsers = {
            'list': ListParser(self),
            'detail': DetailParser(self),
            'comment': CommentParser(self),
        }
        self.downloader = Downloader(config.HEADERS)
        self.storage = Storage(config.MONGO_DATABASE, config.MONGO_HOST, config.MONGO_PORT)
        self.task_queue = TaskQueue(config.REDIS_DB_URL, config.REDIS_DB_DATABASE)

    def save_content(self, content: Document, type_: str):
        self.storage.save_content(content, type_)

    def append_url(self, url: str, type_: str, reference: str):
        self.task_queue.push_task(Task(url, type_, reference))

    def run(self) -> None:
        while True:
            task = self.task_queue.get_top_task('detail')
            if task is None:
                task = self.task_queue.get_top_task('list')
            # if task is None:
            #     task = self.task_queue.get_top_task('comment')

            if task is None:
                break

            content = self.downloader.download_url(task.url, task.reference)
            try:
                self.parsers[task.type_].parse(task.url, content)
            except Exception as e:
                with open('exception.html', 'w') as ofile:
                    ofile.write(content)
                logger.error(f'Parse failed with error:')
                logger.exception(e)
                raise

            self.task_queue.drop_top_task(task.type_)

            # 等待指定的秒数+-2s
            delay = config.DOWNLOAD_DELAY + random.randint(-20, 20) / 10
            logger.info(f'Delay for {delay} seconds.')
            time.sleep(delay)

    def _get_top_task(self) -> Optional[Task]:
        result = self.task_queue.get_top_task('list')
        if result is not None:
            return result

        result = self.task_queue.get_top_task('detail')
        if result is not None:
            return result

        result = self.task_queue.get_top_task('comment')
        if result is not None:
            return result

        return None
