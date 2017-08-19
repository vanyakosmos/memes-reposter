import requests

from telegram_autoposter.fetcher import Fetcher
from settings import reddit_settings, FETCH_LIMIT

username = reddit_settings['username']


class RedditFetcher(Fetcher):
    def fetch(self, subreddit):
        self.logger.debug(f'Subreddit: "{subreddit}". Fetching...')
        url = f"https://reddit.com/r/{subreddit}/top/.json?limit={FETCH_LIMIT}"
        headers = {
            "User-Agent": f"ChangeMeClient/0.1 by {username}"
        }
        response = requests.request(method='GET', url=url, headers=headers)
        json = response.json()

        self.logger.debug(f'Fetched. Code: {response.status_code}')
        data = []
        if response.status_code == 200:
            data = json['data']['children']
        return data
