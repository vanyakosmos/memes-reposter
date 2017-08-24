from typing import List, Dict

from core import store


class RedditStore(store.RedisStore):
    def __init__(self, prefix, url, clear_age):
        super().__init__(prefix, url, clear_age)
        self.key_subreddits = prefix + ':subreddits'

    # subreddits
    def get(self) -> Dict[str, int]:
        res = self.client.hgetall(self.key_subreddits)
        subreddits = {}
        for name, score in res.items():
            subreddits[name.decode('utf-8')] = int(score)
        return subreddits

    def add(self, subreddits: Dict[str, int]):
        self.client.hmset(self.key_subreddits, subreddits)

    def remove(self, subreddits: List[str]):
        self.client.hdel(self.key_subreddits, *subreddits)
