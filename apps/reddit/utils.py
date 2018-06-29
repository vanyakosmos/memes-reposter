import re

import requests


GIPHY_REGEX = re.compile(r'^https?://(?:media|i)\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$')
GFYCAT_REGEX = re.compile(r'^https?://(?:\w+\.)?gfycat.com/(?:\w+/)*(\w+)(?:\.mp4)?$')
IMGUR_GIF_REGEX = re.compile(r'^(.+)\.(gifv?|mp4)$')
REDDIT_REGEX = re.compile(r'^https?://(www.)?reddit.com/.*$')
TRASH_REGEX = re.compile(r'[^\w\s]')


def has_ext(file: str, *exts: str):
    return any(map(file.endswith, exts))


def get_gfycat_url(gif_url):
    api_url = GFYCAT_REGEX.sub(r'https://api.gfycat.com/v1/gfycats/\g<1>', gif_url)
    res = requests.get(api_url)
    item = res.json()
    url = item['gfyItem']['mp4Url']
    return url


def get_media(item: dict) -> dict:
    res = {
        'media': item['link'],
        'type': 'link',  # link | photo | video | text
        'text': '',
    }
    domain = item['domain']

    # === IMAGES ===
    if has_ext(item['url'], '.png', '.jpg', '.jpeg'):
        res['type'] = 'photo'
        res['media'] = item['url']
    # imgur single image post
    elif domain in ('imgur.com', 'm.imgur.com') and not IMGUR_GIF_REGEX.match(item['url']):
        res['type'] = 'photo'
        res['media'] = item['url'] + '.png'

    # === VIDEOS ===
    elif domain == 'gfycat.com':
        res['type'] = 'video'
        res['media'] = get_gfycat_url(item['url'])
    elif domain in ('media.giphy.com', 'i.giphy.com'):
        res['type'] = 'video'
        gif_id = GIPHY_REGEX.findall(item['url'])[0]
        res['media'] = f'https://i.giphy.com/media/{gif_id}/giphy.mp4'
    elif domain in ('imgur.com', 'm.imgur.com', 'i.imgur.com'):
        res['type'] = 'video'
        res['media'] = IMGUR_GIF_REGEX.sub('\g<1>.mp4', item['url'])
    elif domain == 'v.redd.it':
        res['type'] = 'video'
        res['media'] = item['media']['reddit_video']['fallback_url']

    # === TEXTS ===
    elif REDDIT_REGEX.match(item['url']):
        res['type'] = 'text'
        res['text'] = item['selftext']

    return res
