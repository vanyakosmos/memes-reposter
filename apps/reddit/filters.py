import logging
import re
from functools import reduce
from typing import List

from apps.core.filters import log_size
from .models import Post, Subreddit


logger = logging.getLogger(__name__)


@log_size
def score_filter(posts: List[Post], subreddit: Subreddit):
    """Score pass."""
    new_posts = []
    for post in posts:
        if post.score > subreddit.score_limit:
            new_posts.append(post)
        elif post.score > subreddit.low_score_limit and subreddit.on_moderation:
            post.status = Post.STATUS_PENDING
            new_posts.append(post)
    return new_posts


@log_size
def nsfw_filter(posts: List[Post], subreddit: Subreddit):
    """NSFW pass."""
    return [post for post in posts if subreddit.pass_nsfw or not post.nsfw]


@log_size
def keywords_filter(posts: List[Post], subreddit: Subreddit):
    """Filter out posts with forbidden words in title."""
    keywords = set(subreddit.forbidden_keywords.lower().split(','))
    res = []
    for post in posts:
        title = post.title.lower()
        title = re.sub(r'[^\w\s]', '', title)
        terms = title.split()
        if not any(map(lambda k: k in keywords, terms)):
            res.append(post)
    return res


@log_size
def links_filter(posts: List[Post], _: Subreddit):
    return list(filter(lambda p: not p.not_media, posts))


def apply_filters(posts: List[Post], subreddit: Subreddit) -> iter:
    filters = [
        score_filter,
        nsfw_filter,
        keywords_filter,
        links_filter,
    ]
    posts = reduce(lambda ps, f: f(ps, subreddit), filters, posts)
    return posts
