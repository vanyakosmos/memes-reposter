import logging
import re
from html import unescape

import requests


logger = logging.getLogger(__name__)

GIPHY_REGEX = re.compile(r'^https?://(?:media|i)\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$')
GFYCAT_REGEX = re.compile(r'^https?://(?:\w+\.)?gfycat.com/(?:\w+/)*(\w+)(?:\.mp4)?$')
IMGUR_GIF_REGEX = re.compile(r'^(.+)\.gifv?$')
REDDIT_REGEX = re.compile(r'^https?://(www.)?reddit.com/.*$')


def get_gfycat_url(gif_url):
    api_url = GFYCAT_REGEX.sub(r'https://api.gfycat.com/v1/gfycats/\g<1>', gif_url)
    res = requests.get(api_url)
    item = res.json()
    url = item['gfyItem']['mp4Url']
    return url


class Post(object):
    def __init__(self, item):
        meta = self._get_meta(item)
        media_url, type, text = meta['url'], meta['type'], meta['text'],

        self.id = item['id']
        self.subreddit = item['subreddit']
        self.title = unescape(item['title'])
        self.score = int(item['score'])
        self.url = item['url']
        self.media_url = media_url
        self.comments = 'https://redd.it/' + item['id']
        self.comments_full = f'https://reddit.com/r/{item["subreddit"]}/comments/{item["id"]}'
        self.created_at = int(item['created_utc'])
        self.type = type
        self.nsfw = item['over_18']
        self.text = text

    def __str__(self):
        return (f'Post(id:{repr(self.id)} t:{repr(self.title)} type:{repr(self.type)} '
                f'url:{repr(self.url)} murl:{repr(self.media_url)}')

    def __repr__(self):
        return str(self)

    def _has_ext(self, file: str, *exts):
        return any([file.endswith(ext) for ext in exts])

    def _get_meta(self, item: dict) -> dict:
        item['url'] = re.sub(r'\?.*$', '', item['url'])  # get rid of querystring
        result = {
            'type': 'link',
            'url': item['url'],
            'text': '',
        }
        domain = item['domain']

        # === IMAGES ===
        if self._has_ext(item['url'], '.png', '.jpg', '.jpeg'):
            result['type'] = 'photo'
            result['url'] = item['url']
        # imgur single image post
        elif domain in ('imgur.com', 'm.imgur.com'):
            result['url'] = item['url'] + '.png'
            result['type'] = 'photo'

        # === VIDEOS ===
        elif domain == 'gfycat.com':
            result['url'] = get_gfycat_url(item['url'])
            result['type'] = 'video'
        elif domain in ('media.giphy.com', 'i.giphy.com'):
            gif_id = GIPHY_REGEX.findall(item['url'])[0]
            result['url'] = f'https://i.giphy.com/media/{gif_id}/giphy.mp4'
            result['type'] = 'video'
        elif domain == 'i.imgur.com':
            result['url'] = IMGUR_GIF_REGEX.sub('\g<1>.mp4', item['url'])
            result['type'] = 'video'
        elif domain == 'v.redd.it':
            result['type'] = 'video'
            result['url'] = item['url'] + '/DASH_600_K'

        # === TEXTS ===
        elif REDDIT_REGEX.match(item['url']):
            result['type'] = 'text'
            result['text'] = item['selftext']

        return result
