import logging
from functools import reduce
from typing import List

from django.db.models import Q

from core.filters import log_size
from .models import Post, Subreddit

logger = logging.getLogger(__name__)


@log_size
def score_filter(posts: List[Post], subreddit: Subreddit):
    """Score pass."""
    new_posts = []
    for post in posts:
        if post.score > subreddit.score_limit_repost:
            new_posts.append(post)
        elif post.score > subreddit.score_limit:
            post.status = Post.STATUS_PENDING
            new_posts.append(post)
    return new_posts


@log_size
def nsfw_filter(posts: List[Post], subreddit: Subreddit):
    """NSFW pass."""
    return [post for post in posts if subreddit.pass_nsfw or not post.nsfw]


@log_size
def inner_unique_filter(posts: List[Post], _: Subreddit):
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
def unique_filter(posts: List[Post], _: Subreddit):
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
    new_posts = []
    for post in posts:
        try:
            old_post = Post.objects.get(Q(reddit_id=post.reddit_id) | Q(link=post.url))
        except Post.DoesNotExist:
            old_post = None

        if old_post:
            if old_post.status == Post.STATUS_PENDING and post.status == Post.STATUS_ACCEPTED:
                old_post.status = Post.STATUS_ACCEPTED
                old_post.score = post.score
                new_posts.append(old_post)
        else:
            new_posts.append(post)
    return new_posts


@log_size
def keywords_filter(posts: List[Post], subreddit: Subreddit):
    """Filter out posts with forbidden words in title."""
    keywords = subreddit.forbidden_keywords_set
    return [post for post in posts if not any(map(lambda k: k in keywords, post.title_terms))]


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
