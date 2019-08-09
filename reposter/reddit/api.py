import logging

import requests

logger = logging.getLogger(__name__)
HEADERS = {"User-Agent": f"Mozilla/2000"}


def get_reddit_url(*args, api=True):
    base = 'https://reddit.com/r'
    url = '/'.join([base, *args])
    if api:
        url += '/.json'
    return url


def get_about(subreddit):
    url = get_reddit_url(subreddit, 'about')
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    return data['data']


def get_posts(subreddit, limit: int):
    logger.debug(f'Subreddit: "{subreddit}". Fetching...')
    url = get_reddit_url(subreddit, 'top')
    res = requests.get(url, params={'limit': limit}, headers=HEADERS)
    logger.info(f'Fetched data from "{subreddit}". Code: {res.status_code}')
    data = res.json()
    posts = []
    if res.status_code == 200:
        posts = [p['data'] for p in data['data']['children']]
    return posts
