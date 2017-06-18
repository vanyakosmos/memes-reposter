from autoposter import AbstractFilter
from settings import BANNED_TAGS
from .fetcher import AlbumFetcher
from .database import AbstractDB
from .wrappers import Post


class PostsFilter(AbstractFilter):
    def __init__(self, db: AbstractDB, client_id: str):
        super().__init__(db)
        self.client_id = client_id

    def filter(self, posts):
        """
        Args:
            posts (List[dict]): Posts obtained from Imgur gallery.

        Returns:
            List[Post]: list of Post objects.
        """
        filtered_posts = []
        album_fetcher = AlbumFetcher(client_id=self.client_id)
        for post_dict in posts:
            post = Post(post_dict, album_fetcher)

            if post.id in self.db:
                continue

            for bad_tag in BANNED_TAGS:
                if bad_tag in post.tags:
                    continue

            if post.valid:
                filtered_posts.append(post)

        return filtered_posts
