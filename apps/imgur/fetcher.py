import logging
import os
from pprint import pprint
from typing import List

import requests
from dotenv import find_dotenv, load_dotenv

from apps.imgur.models import Post


logger = logging.getLogger(__name__)


def fetch(client_id: str, limit=100):
    section = 'hot'  # hot | top | user
    sort = 'viral'  # viral | top | time | rising (only available with user section)
    show_viral = 'true'
    show_mature = 'true'
    album_previews = 'false'

    url = f'https://api.imgur.com/3/gallery/{section}/{sort}'
    querystring = {
        "showViral": f"{show_viral}",
        "mature": f"{show_mature}",
        "album_previews": f"{album_previews}"
    }
    headers = {'authorization': f'Client-ID {client_id}'}
    response = requests.get(url, headers=headers, params=querystring)
    logger.info(f'Fetched imgur posts. Code: {response.status_code}')
    posts = []
    if response.status_code == 200:
        json = response.json()
        posts = json['data'][:limit]
    logger.debug(f"fetched imgur posts: {len(posts)}")
    return posts


def fetch_album(client_id, post_id):
    url = f'https://api.imgur.com/3/album/{post_id}/images'
    headers = {'authorization': f'Client-ID {client_id}'}
    response = requests.request("GET", url, headers=headers)
    logger.debug(f'Fetched album {post_id}. Code: {response.status_code}')
    if response.status_code != 200:
        return
    json = response.json()
    return json['data']


def populate_albums(posts: List[Post], client_id: str, limit=10):
    for post in posts:
        if post.is_album:
            images = fetch_album(client_id, post.imgur_id)
            if images is None:
                continue
            post.medias = images[:limit]


def main():
    load_dotenv(find_dotenv())
    a = fetch_album(os.getenv('IMGUR_CLIENT_ID'), '7FBFWIP')
    a = a[:4]
    pprint(a)


if __name__ == '__main__':
    main()
