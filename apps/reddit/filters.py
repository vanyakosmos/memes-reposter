import logging
from functools import reduce
from typing import List
from functools import wraps

from django.db.models import Q

from apps.reddit.models import Post, Subreddit, RedditConfig


logger = logging.getLogger(__name__)


def log_size(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug('Filter %s > %d', func.__name__, len(result))
        return result
    return wrapper


@log_size
def score_filter(posts: List[Post], subreddit: Subreddit):
    """Score pass."""
    return [
        post for post in posts
        if post.score > subreddit.score_limit
    ]


@log_size
def nsfw_filter(posts: List[Post], subreddit: Subreddit):
    """NSFW pass."""
    return [
        post for post in posts
        if subreddit.pass_nsfw or not post.nsfw
    ]


@log_size
def inner_unique_filter(posts: List[Post], _: Subreddit):
    """Check that urls are unique inside current posts bulk."""
    res = []
    urls = set()
    for post in posts:
        if post.link not in urls:
            res.append(post)
            urls.add(post.link)
    return res


@log_size
def unique_filter(posts: List[Post], _: Subreddit):
    """Filter out published posts."""
    return [
        post for post in posts
        if not Post.objects.filter(Q(reddit_id=post.reddit_id) | Q(link=post.link)).exists()
    ]


@log_size
def keywords_filter(posts: List[Post], _: Subreddit):
    """Filter out posts with forbidden words in title."""
    config = RedditConfig.get_solo()
    keywords = config.forbidden_keywords_set
    return [
        post for post in posts
        if not any(map(lambda k: k in keywords, post.title_terms))
    ]


def apply_filters(posts: List[Post], subreddit: Subreddit) -> iter:
    filters = [
        score_filter,
        nsfw_filter,
        inner_unique_filter,
        unique_filter,
        keywords_filter,
    ]
    posts = reduce(lambda ps, f: f(ps, subreddit), filters, posts)
    return posts
