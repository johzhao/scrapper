from typing import Optional

import redis

from model.task import Task

TASK_KEY = 'scrapper_tasks'


class TaskQueue:

    def __init__(self, redis_url: str, db: int):
        self.redis = redis.Redis.from_url(redis_url, db=db)

    def push_task(self, task: Task):
        self.redis.rpush(self._get_task_key(task.type_), str(task))

    def get_top_task(self, type_: str) -> Optional[Task]:
        key = self._get_task_key(type_)
        count = self.redis.llen(key)
        if count == 0:
            return None

        data = self.redis.lindex(key, 0)
        return Task.from_string(data)

    def drop_top_task(self, type_: str):
        self.redis.lpop(self._get_task_key(type_))

    @staticmethod
    def _get_task_key(type_: str) -> str:
        return f'{type_}_tasks'
