from typing import List

from telegram_autoposter.modeller import Modeller

from .models import Post


class RedditModeller(Modeller):
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
