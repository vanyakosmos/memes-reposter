from html import unescape
import re


GIPHY_REGEX = re.compile(r'^https?://media\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$')
GFYCAT_REGEX = re.compile(r'^https?://(?:\w+\.)?gfycat.com/(?:\w+/)*(\w+)(?:\.mp4)?$')
IMGUR_REGEX = re.compile(r'^https?://(m\.)?imgur.com/[^/]+$')
IMGUR2_REGEX = re.compile(r'^https?://imgur.com/r/[^/]+/[^/]+$')
REDDIT_REGEX = re.compile(r'^https?://v\.redd\.it/[^/]+$')
REDDIT2_REGEX = re.compile(r'^https?://(www.)?reddit.com/.*$')


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
        item['url'] = re.sub(r'\?.*$', '', item['url'])
        result = {
            'type': 'link',
            'url': item['url'],
            'text': '',
        }

        # regular image
        if self._has_ext(item['url'], '.png', '.jpg'):
            result['type'] = 'photo'
            result['url'] = item['url']
        # gficat
        elif item['domain'] == 'gfycat.com':
            url = GFYCAT_REGEX.sub(r'https://giant.gfycat.com/\g<1>.mp4', item['url'])
            result['type'] = 'video'
            result['url'] = url
        # giphy video. must be on because of custom giphy player
        elif GIPHY_REGEX.match(item['url']):
            gif_id = GIPHY_REGEX.findall(item['url'])[0]
            result['type'] = 'video'
            result['url'] = f'https://i.giphy.com/media/{gif_id}/giphy.mp4'

        # video with explicit extension
        elif self._has_ext(item['url'], '.gif', '.gifv'):
            if self._has_ext(item['url'], '.gifv') and re.match(r'(i.)?imgur.com', item['domain']):
                result['url'] = re.sub(r'^(.+)\.gifv?$', '\g<1>.mp4', item['url'])
            else:
                result['url'] = item['url']
            result['type'] = 'video'

        # imgur single image post
        elif IMGUR_REGEX.match(item['url']):
            url = item['url'] + '.png'
            result['type'] = 'photo'
            result['url'] = url

        # imgur single image post with reddit tag
        elif IMGUR2_REGEX.match(item['url']):
            url = re.sub(r'^https?://imgur.com/r/[^/]+/([^/]+)$',
                         r'https://imgur.com/\g<1>.png',
                         item['url'])
            result['type'] = 'photo'
            result['url'] = url

        # gfycat video
        elif item['domain'] == 'gfycat.com':
            url = re.sub(r'https?://gfycat.com/(.+)',
                         r'https://fat.gfycat.com/\g<1>.mp4',
                         item['url'])
            result['type'] = 'video'
            result['url'] = url

        # reddit hosted video
        elif REDDIT_REGEX.match(item['url']):
            url = item['url'] + '/DASH_600_K'
            result['type'] = 'video'
            result['url'] = url

        # text post from reddit
        elif REDDIT2_REGEX.match(item['url']):
            result['type'] = 'text'
            result['text'] = item['selftext']

        return result
