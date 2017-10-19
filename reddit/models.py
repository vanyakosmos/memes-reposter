from html import unescape
import re


class Post(object):
    def __init__(self, item):
        meta = self._get_meta(item)
        url, type, text = meta['url'], meta['type'], meta['text'],

        self.id = item['id']
        self.subreddit = item['subreddit']
        self.title = unescape(item['title'])
        self.score = int(item['score'])
        self.url = url
        self.comments = 'https://redd.it/' + item['id']
        self.created_at = int(item['created_utc'])
        self.type = type
        self.nsfw = item['over_18']
        self.text = text

    def __str__(self):
        return f'Post(id="{self.id}", url="{self.url}")'

    def __repr__(self):
        return f'Post(id="{self.id}", title="{self.title}, url="{self.url}"")'

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
            # return 'photo', item['url']

        # giphy video. must be on because of custom giphy player
        elif re.match(r'^https?://media\.giphy\.com/media/(\w+)/giphy\.(?:gif|mp4)$', item['url']):
            gif_id = re.findall(r'^https?://media.giphy.com/media/(\w+)/giphy.(?:gif|mp4)', item['url'])[0]
            # print('giphy', gif_id)
            result['type'] = 'video'
            result['url'] = f'https://i.giphy.com/media/{gif_id}/giphy.mp4'
            # return 'video', f'https://i.giphy.com/media/{gif_id}/giphy.mp4'

        # video with explicit extension
        elif self._has_ext(item['url'], '.gif', '.gifv'):
            if self._has_ext(item['url'], '.gifv') and re.match(r'(i.)?imgur.com', item['domain']):
                result['url'] = re.sub(r'^(.+)\.gifv?$', '\g<1>.mp4', item['url'])
            else:
                result['url'] = item['url']
            result['type'] = 'video'
            # return 'video', url

        # imgur single image post
        elif re.match(r'^https?://(m\.)?imgur.com/[^/]+$', item['url']):
            url = item['url'] + '.png'
            result['type'] = 'photo'
            result['url'] = url
            # return 'photo', url

        # imgur single image post with reddit tag
        elif re.match(r'^https?://imgur.com/r/[^/]+/[^/]+$', item['url']):
            url = re.sub(r'^https?://imgur.com/r/[^/]+/([^/]+)$',
                         r'https://imgur.com/\g<1>.png',
                         item['url'])
            result['type'] = 'photo'
            result['url'] = url
            # return 'photo', url

        # gfycat video
        elif item['domain'] == 'gfycat.com':
            url = re.sub(r'https?://gfycat.com/(.+)',
                         r'https://thumbs.gfycat.com/\g<1>-size_restricted.gif',
                         item['url'])
            result['type'] = 'video'
            result['url'] = url
            # return 'video', url

        # reddit hosted video
        elif re.match(r'^https?://v\.redd\.it/[^/]+$', item['url']):
            url = item['url'] + '/DASH_600_K'
            result['type'] = 'video'
            result['url'] = url
            # return 'video', url

        # text post from reddit
        elif re.match(r'^https?://(www.)?reddit.com/.*$', item['url']):
            result['type'] = 'text'
            result['text'] = item['selftext']

        return result
