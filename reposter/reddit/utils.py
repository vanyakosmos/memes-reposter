import logging
import re
from typing import List

import requests

logger = logging.getLogger(__name__)

GIPHY_REGEX = re.compile(r'^https?://(?:media|i)\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$')
GFYCAT_REGEX = re.compile(r'^https?://(?:\w+\.)?gfycat.com/(?:\w+/)*(\w+)(?:\.mp4)?$')
IMGUR_GIF_REGEX = re.compile(r'^(.+)\.(gifv?|mp4)$')
GIF_REGEX = re.compile(r'^https?://.*\.gif$')


def has_ext(file: str, *exts: str):
    return any(map(file.endswith, exts))


def get_gfycat_url(gif_url):
    api_url = GFYCAT_REGEX.sub(r'https://api.gfycat.com/v1/gfycats/\g<1>', gif_url)
    res = requests.get(api_url)
    try:
        item = res.json()
    except Exception as e:
        logger.error(e)
        return
    url = item['gfyItem']['mp4Url']
    return url


def get_photo_url(data: dict):
    if has_ext(data['url'], '.png', '.jpg', '.jpeg'):
        return data['url']
    elif data['domain'] in ('imgur.com', 'm.imgur.com') and not IMGUR_GIF_REGEX.match(data['url']):
        return data['url'] + '.png'


def get_video_url(data: dict):
    domain = data['domain']
    if domain == 'gfycat.com':
        return get_gfycat_url(data['url'])

    elif domain in ('media.giphy.com', 'i.giphy.com'):
        gif_id = GIPHY_REGEX.findall(data['url'])[0]
        return f'https://i.giphy.com/media/{gif_id}/giphy.mp4'

    elif domain in ('imgur.com', 'm.imgur.com', 'i.imgur.com'):
        return IMGUR_GIF_REGEX.sub(r'\g<1>.mp4', data['url'])

    elif domain == 'v.redd.it':
        media = data['media']
        if media:
            return data['media']['reddit_video']['fallback_url']


def get_gif_url(data: dict):
    if GIF_REGEX.match(data['url']):
        return data['url']


def format_field_pairs(obj, fields: List[str]):
    return ', '.join([f'{field}="{getattr(obj, field, None)}"' for field in fields])
