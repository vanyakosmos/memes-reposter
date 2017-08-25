from urllib.parse import unquote
import re


class Post(object):
    def __init__(self, item):
        type, url = self._get_type_and_url(item)

        self.id = item['id']
        self.subreddit = item['subreddit']
        self.title = unquote(item['title'])
        self.score = int(item['score'])
        self.url = url
        self.comments = 'https://redd.it/' + item['id']
        self.created_at = int(item['created_utc'])
        self.type = type

    def __str__(self):
        return f'Post(id="{self.id}", url="{self.url}")'

    def __repr__(self):
        return f'Post(id="{self.id}", title="{self.title}, url="{self.url}"")'

    def _has_ext(self, file: str, *exts):
        return any([file.endswith(ext) for ext in exts])

    def _get_type_and_url(self, item: dict) -> (str, str):
        item['url'] = re.sub(r'\?.*$', '', item['url'])
        if self._has_ext(item['url'], '.png', '.jpg'):
            return 'photo', item['url']

        elif self._has_ext(item['url'], '.gif', '.gifv'):
            if self._has_ext(item['url'], '.gifv') and re.match(r'(i.)?imgur.com', item['domain']):
                url = re.sub(r'^(.+)\.gifv?$', '\g<1>.mp4', item['url'])
            else:
                url = item['url']
            return 'video', url

        elif re.match(r'^https?://imgur.com/[^/]+$', item['url']):
            url = item['url'] + '.png'
            return 'photo', url

        elif re.match(r'^https?://imgur.com/r/[^/]+/[^/]+$', item['url']):
            url = re.sub(r'^https?://imgur.com/r/[^/]+/([^/]+)$',
                         r'https://imgur.com/\g<1>.png',
                         item['url'])
            return 'photo', url

        elif item['domain'] == 'gfycat.com':
            url = re.sub(r'https?://gfycat.com/(.+)',
                         r'https://thumbs.gfycat.com/\g<1>-size_restricted.gif',
                         item['url'])
            return 'video', url
        else:
            return 'link', item['url']
