import logging
from pprint import pprint

import requests


logger = logging.getLogger(__name__)


def fetch(subreddit: str, limit=20):
    logger.debug(f'Subreddit: "{subreddit}". Fetching...')
    url = f"https://reddit.com/r/{subreddit}/top/.json?limit={limit}"
    headers = {
        "User-Agent": f"Mozilla/2000"
    }
    response = requests.request(method='GET', url=url, headers=headers)
    logger.info(f'Fetched data from "{subreddit}". Code: {response.status_code}')
    data = response.json()
    posts = []
    if response.status_code == 200:
        posts = [p['data'] for p in data['data']['children']]
    return posts


def main():
    res = fetch('funny')
    pprint(res)


if __name__ == '__main__':
    main()
