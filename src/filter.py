import logging
from typing import List

from settings import BANNED_TAGS
from src.database import AbstractDB
from src.post import Post


logger = logging.getLogger(__name__)


def filter_posts(posts: List[dict], db: AbstractDB) -> List[Post]:
    """
    Args:
        posts (List[dict]): Posts obtained from Imgur gallery.
        db (AbstractDB): Database that store post ids and its datetime.
    
    Returns:
        List[Post]
    """
    filtered_posts = []

    for post_dict in posts:
        post = Post(post_dict)

        if post.id in db:
            continue

        for bad_tag in BANNED_TAGS:
            if bad_tag in post.tags:
                continue

        if post.valid:
            filtered_posts.append(post)

    return filtered_posts
