import logging
from functools import reduce
from typing import List

from django.db.models import Q

from core.filters import log_size
from .models import Post, Subreddit

logger = logging.getLogger(__name__)


class NoPostsException(Exception):
    pass


def get_subreddit(posts: List[Post]):
    if len(posts) == 0:
        raise NoPostsException()
    return posts[0].subreddit


@log_size
def score_filter(posts: List[Post]):
    """Score pass."""
    new_posts = []
    subreddit = get_subreddit(posts)
    for post in posts:
        if post.score > subreddit.score_limit_repost:
            new_posts.append(post)
        elif post.score > subreddit.score_limit:
            post.status = Post.PENDING
            new_posts.append(post)
    return new_posts


@log_size
def nsfw_filter(posts: List[Post]):
    """NSFW pass."""
    subreddit = get_subreddit(posts)
    return [post for post in posts if subreddit.pass_nsfw or not post.nsfw]


@log_size
def inner_unique_filter(posts: List[Post]):
    """Check that urls are unique inside current posts bulk."""
    res = []
    urls = set()
    for post in posts:
        post_urls = {post.url, post.photo_url, post.video_url} - {None}
        if all(url not in urls for url in post_urls):
            res.append(post)
        urls |= post_urls
    return res


@log_size
def unique_filter(posts: List[Post]):
    """
    Filter out published posts.
    If found old post with same id:
        if old post is pending and new post is accepted
            make old post accepted and add it to list
        if old post is rejected or already accepted
            do nothing
    if not found old post:
        add new post to list
    """
    # todo: filter for specific subreddit
    new_posts = []
    for post in posts:
        try:
            old_post = Post.objects.get(Q(reddit_id=post.reddit_id) | Q(url=post.url))
        except Post.DoesNotExist:
            old_post = None

        if old_post:
            if old_post.status == Post.PENDING and post.status == Post.ACCEPTED:
                old_post.status = Post.ACCEPTED
                old_post.score = post.score
                new_posts.append(old_post)
        else:
            new_posts.append(post)
    return new_posts


@log_size
def keywords_filter(posts: List[Post]):
    """Filter out posts with forbidden words in title."""
    subreddit = get_subreddit(posts)
    keywords = subreddit.forbidden_keywords_set
    return [post for post in posts if not any(map(lambda k: k in keywords, post.tokens))]


def apply_filters(posts: List[Post], subreddit: Subreddit) -> iter:
    filters = [
        score_filter,
        nsfw_filter,
        inner_unique_filter,
        unique_filter,
        keywords_filter,
    ]
    try:
        posts = reduce(lambda ps, f: f(ps), filters, posts)
    except NoPostsException:
        return []
    return posts
