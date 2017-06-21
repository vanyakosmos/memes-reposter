import unittest

import redis
import time

from src.database import RedisDB, RedditRedisDB


class TestRedisDB(unittest.TestCase):
    def setUp(self):
        self.DATA = 'test:data'
        self.DATES = 'test:dates'
        self.client = redis.StrictRedis(db=15)
        self.database = RedisDB('test', self.client)
        now = time.time()
        self.keys = {
            'id1': now - 100,
            'id2': now - 123,
            'id3': now - 225,
            'id4': now - 256,
        }
        for key, date in self.keys.items():
            self.client.hset('test:data', key, date)
            self.client.sadd('test:dates', date)

    def tearDown(self):
        self.client.flushdb()

    def test_add(self):
        now = time.time()
        self.database.add('id5', now + 123)
        self.assertEqual(self.client.hget(self.DATA, 'id5'), str(now+123).encode('ascii'))
        self.assertEqual(self.client.hlen(self.DATA), 5)
        self.assertEqual(self.client.scard(self.DATES), 5)

        self.database.add('id5', now + 125)
        self.assertEqual(self.client.hget(self.DATA, 'id5'), str(now + 125).encode('ascii'))
        self.assertEqual(self.client.hlen(self.DATA), 5)
        self.assertEqual(self.client.scard(self.DATES), 6)

    def test_keys(self):
        self.assertSetEqual(self.database.keys(), set(self.keys.keys()))

        self.client.hset(self.DATA, 'id1', 123)
        self.assertSetEqual(self.database.keys(), set(self.keys.keys()))

        self.client.hset(self.DATA, 'id5', 123)
        self.assertSetEqual(self.database.keys(), set(self.keys.keys()) | {'id5'})

    def test_clear(self):
        self.database.clear(1300)
        self.assertEqual(self.client.hlen(self.DATA), 4)
        self.assertEqual(self.client.scard(self.DATES), 4)

        self.database.clear(130)
        self.assertEqual(self.client.hlen(self.DATA), 2)
        self.assertEqual(self.client.scard(self.DATES), 2)

        self.database.clear(0)
        self.assertEqual(self.client.hlen(self.DATA), 0)
        self.assertEqual(self.client.scard(self.DATES), 0)

    def test_dates_list(self):
        l = self.database.dates_list()
        self.assertEqual(len(l), 4)
        self.assertEqual(l, sorted(l))
        self.assertEqual(type(l[0]), int)

        self.client.sadd(self.DATES, '124.543')
        l = self.database.dates_list()
        self.assertEqual(len(l), 5)
        self.assertEqual(l, sorted(l))
        self.assertEqual(type(l[0]), int)


class TestRedditRedisDB(unittest.TestCase):
    def setUp(self):
        self.SUBREDDIT = 'test:subreddits'
        self.client = redis.StrictRedis(db=15)
        self.database = RedditRedisDB('test', self.client)

        self.subreddits = {
            'pics': 100,
            'gifs': 200,
        }

        for name, score in self.subreddits.items():
            self.client.hset(self.SUBREDDIT, name, score)

    def tearDown(self):
        self.client.flushdb()

    def test_add_subreddit(self):
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 2)

        self.database.add_subreddit('funny', 1234)
        self.assertEqual(self.client.hget(self.SUBREDDIT, 'funny'), b'1234')
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 3)

        self.database.add_subreddit('funny', 2345)
        self.assertEqual(self.client.hget(self.SUBREDDIT, 'funny'), b'2345')
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 3)

    def test_remove_subreddit(self):
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 2)

        self.database.remove_subreddit('funny')
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 2)

        self.client.hset(self.SUBREDDIT, 'funny', 100)
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 3)

        self.database.remove_subreddit('funny')
        self.database.remove_subreddit('pics')
        self.assertEqual(self.client.hlen(self.SUBREDDIT), 1)

    def test_get_subreddits(self):
        res = self.database.get_subreddits()
        self.assertEqual(self.subreddits, res)

        self.client.hset(self.SUBREDDIT, 'funny', 555)
        res = self.database.get_subreddits()
        self.subreddits['funny'] = 555
        self.assertEqual(self.subreddits, res)

