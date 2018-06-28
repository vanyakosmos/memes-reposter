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
    json = response.json()

    logger.debug(f'Fetched. Code: {response.status_code}')
    data = []
    if response.status_code == 200:
        data = [p['data'] for p in json['data']['children']]
    return data


def main():
    res = fetch('funny')
    pprint(res)


if __name__ == '__main__':
    main()
