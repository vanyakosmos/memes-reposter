from time import time
from typing import Dict, List

from core import store
from .models import Post


class RedditStore(store.MongoStore):
    def __init__(self, name, url, clear_age):
        super().__init__(name, url, clear_age)
        self.subs = self.get_collection('subs')

    def get(self) -> Dict[str, int]:
        subs = self.subs.find()
        res = {
            s['name']: s['limit']
            for s in subs
        }
        return res

    def add(self, subreddits: Dict[str, int]):
        for name, limit in subreddits.items():
            self.subs.update_one(
                {'name': name},
                {'$set': {'name': name, 'limit': limit}},
                upsert=True)

    def remove(self, subreddits: List[str]):
        self.subs.delete_many({
            'name': {
                '$in': subreddits
            }
        })

    def save_post(self, post: Post):
        self.posts.insert_one({
            'id': post.id,
            'title': post.title,
            'subreddit': post.subreddit,
            'url': post.url,
            'comments': post.comments,
            'type': post.type,
            'timestamp': time(),
            'claps': 0,
        })

    def has_urls(self, urls):
        posts = self.posts.find()
        posts_urls = {
            p.get('url', None)
            for p in posts
        }
        res = [
            url in posts_urls
            for url in urls
        ]
        return res

    def get_post(self, post_id):
        post = self.posts.find_one({'id': post_id})
        return post

    def clap(self, post_id):
        self.posts.update_one({'id': post_id}, {'$inc': {'claps': 1}})
