from typing import Dict, List

from core import store


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
