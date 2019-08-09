from typing import List

from core.post import Post


def filters_posts(chat: 'Chat', posts: List[Post]):
    ks = chat.forbidden_keywords_set
    return [p for p in posts if not any(map(lambda t: t in ks, p.tokens))]
