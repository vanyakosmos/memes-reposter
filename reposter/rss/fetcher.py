import re
from typing import Optional

import feedparser

from .models import Post, RssFeed

IMAGE_TAG = re.compile(r'<img.*src="(.+)".*/>')


class FeedException(Exception):
    pass


def get_picture(post: dict) -> Optional[str]:
    try:
        content = post['content'][0]['value']
    except (KeyError, ValueError, IndexError):
        return
    if not content.startswith('<img'):
        return
    pic_link = IMAGE_TAG.findall(content)[0]  # type: str
    if any(map(pic_link.endswith, ['.png', '.jpg', '.jpeg'])):
        return pic_link


def posts_iter(feed_link: str):
    feed = feedparser.parse(feed_link)
    if feed.get('status', 500) != 200:
        raise FeedException(f"Failed to fetch feed {feed_link}.")
    if feed['bozo'] != 0:
        exc = str(feed.get('bozo_exception', 'none'))
        msg = f"Feed {feed_link} is malformed: {exc}"
        raise FeedException(msg)
    entities = feed.get('entries', [])
    return entities[::-1]


def fetch_posts(feed: RssFeed):
    return [
        Post(
            feed=feed,
            title=post['title'],
            url=post[feed.link_field or 'link'],
            photo_url=get_picture(post),
            comments=post.get('comments', None),
        ) for post in posts_iter(feed.link)
    ]
