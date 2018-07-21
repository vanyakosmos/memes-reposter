import re
from typing import Optional

import feedparser

from .errors import ServiceUnavailableException
from .models import Post


IMAGE_TAG = re.compile(r'<img.*src="(.+)".*/>')


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
        raise ServiceUnavailableException(f"Failed to fetch feed {feed_link}.")
    if feed['bozo'] != 0:
        exc = str(feed.get('bozo_exception', 'none'))
        msg = f"Feed {feed_link} is malformed: {exc}"
        raise ServiceUnavailableException(msg)
    entities = feed.get('entries', [])
    return entities[::-1]


def fetch_posts(feed_link: str, link_field: Optional[str] = None):
    posts = []
    for post in posts_iter(feed_link):
        title = post['title']
        link = post[link_field or 'link']
        pic_link = get_picture(post)
        comments_link = post.get('comments', None)
        p = Post(
            title=title,
            link=link,
            pic_link=pic_link,
            comments_link=comments_link,
        )
        posts.append(p)
    return posts
