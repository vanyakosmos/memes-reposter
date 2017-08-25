from typing import List

from core.modeller import BaseModeller

from .models import Post


class RedditModeller(BaseModeller):
    def model(self, subreddits, *args, **kwargs) -> List[List[Post]]:
        self.logger.debug('Modelling...')
        result = []
        for subreddit in subreddits:
            posts = []
            for item in subreddit:
                post = Post(item['data'])
                posts.append(post)
            result.append(posts)
        return result
