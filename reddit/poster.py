from typing import List

from telegram_autoposter.poster import Poster
from telegram.ext import Updater

from .models import Post
from .store import Store


class RedditPoster(Poster):
    timeout = 30  # seconds

    def __init__(self, channel_id: str, updater: Updater, store: Store):
        super().__init__(channel_id, updater)
        self.store = store

    def post(self, posts: List[Post], *args, **kwargs):
        for post in posts:
            try:
                self.post_one(post)
            except Exception as e:
                self.logger.error(e)

    def post_one(self, post: Post):
        self.logger.debug(post)
        self.store.save_id(post.id)

        if post.type == 'link':
            text = post.title
            text += '\n' + post.url
            text += '\n#' + post.subreddit + ' ' + post.comments
            self.bot.send_message(text=text,
                                  chat_id=self.channel_id,
                                  timeout=self.timeout)
        else:
            text = self.cut_text(post.title)
            text += '\n#' + post.subreddit + ' ' + post.comments
            kwargs = {
                'caption': text,
                'chat_id': self.channel_id,
                'timeout': self.timeout,
            }
            if post.type == 'photo':
                self.bot.send_photo(photo=post.url, **kwargs)
            elif post.type == 'video':
                self.bot.send_video(video=post.url, **kwargs)

    def cut_text(self, text: str, limit=200):
        if text is None:
            return ''
        elif len(text) > limit:
            text = text[:limit - 5]
            without_last = text.split()[:-1]
            text = ' '.join(without_last)
            return text + '...'
        else:
            return text
