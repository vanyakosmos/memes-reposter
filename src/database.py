import time
from typing import Set, List

import redis

from autoposter import AbstractDB


class RedisDB(AbstractDB):
    def __init__(self, name: str, redis_client: redis.StrictRedis):
        super().__init__()
        self.client = redis_client
        self.name = name
        self.DATA = name + ':data'
        self.DATES = name + ':dates'
        self._check()

    def add(self, post_id, datetime):
        self.client.hset(self.DATA, post_id, datetime)
        self.client.sadd(self.DATES, time.time())

    def keys(self) -> Set[str]:
        return {key.decode('utf-8') for key in self.client.hkeys(self.DATA)}

    def clear(self, period: int) -> (int, int):
        now = time.time()

        # remove old posts from hash `data`
        old_posts = []
        for post_id, datetime in self.client.hgetall(self.DATA).items():
            if float(datetime) + period < now:
                old_posts.append(post_id)
        if old_posts:
            self.client.hdel(self.DATA, *old_posts)

        # remove old date marks from set `dates.txt`
        old_date_marks = []
        for datetime in self.client.smembers(self.DATES):
            if float(datetime) + period < now:
                old_date_marks.append(datetime)
        if old_date_marks:
            self.client.srem(self.DATES, *old_date_marks)

        return len(old_posts), self.client.hlen(self.DATA)

    def dates_list(self) -> List[int]:
        return sorted([int(float(a)) for a in self.client.smembers(self.DATES)])

    def _check(self):
        if self.client.exists(self.DATA):
            self.logger.info(self.name + ': Using OLD database')
        else:
            self.logger.info(self.name + ': Using NEW database')


class RedditRedisDB(RedisDB):
    def __init__(self, name: str, redis_client: redis.StrictRedis):
        super().__init__(name, redis_client)
        self.SUBREDDITS = self.name + ':subreddits'

    def add_subreddit(self, subreddit, score):
        self.logger.debug(f'Adding subreddit {subreddit} with score limit {score} to database.')
        self.client.hset(self.SUBREDDITS, subreddit, score)

    def remove_subreddit(self, subreddit):
        self.logger.debug(f'Removing subreddit {subreddit} from database.')
        self.client.hdel(self.SUBREDDITS, subreddit)

    def get_subreddits(self):
        self.logger.debug('Getting subreddits from database.')
        subreddits_scores = self.client.hgetall(self.SUBREDDITS)
        res = {}
        for subreddit, score in subreddits_scores.items():
            res[subreddit.decode('utf-8')] = int(score)
        return res
