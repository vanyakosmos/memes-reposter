from functools import reduce
from typing import List

from apps.core.filters import log_size
from .models import Post, ImgurConfig


@log_size
def score_filter(posts: List[Post], config: ImgurConfig):
    """Score pass."""
    return [
        post for post in posts
        if post.meta.score > config.score_limit
    ]


@log_size
def unique_filter(posts: List[Post], _: ImgurConfig):
    """Filter out published posts."""
    ids_list = [p.imgur_id for p in posts]
    ids_in_db = set(Post.objects.filter(imgur_id__in=ids_list).values_list('imgur_id', flat=True))
    return [
        post for post in posts
        if post.imgur_id not in ids_in_db
    ]


@log_size
def tags_filter(posts: List[Post], config: ImgurConfig):
    # todo: finish
    if config.exclude_mode:
        pass
    else:
        pass
    return posts


def apply_filters(posts: List[Post], config: ImgurConfig) -> iter:
    filters = [
        score_filter,
        unique_filter,
        tags_filter,
    ]
    posts = reduce(lambda ps, f: f(ps, config), filters, posts)
    return posts
