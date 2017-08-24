from telegram import MAX_CAPTION_LENGTH
from telegram.ext import Updater

from core.publisher import BasePublisher
from core.store import IdStore
from .models import Post


class RedditPublisher(BasePublisher):
    def __init__(self, channel_id: str, updater: Updater, store: IdStore):
        super().__init__(channel_id, updater)
        self.store = store
        self.timeout = 60  # seconds

    def publish(self, post: Post, *args, **kwargs):
        self.store.save_id(post.id)
        self.logger.debug(post)

        try:
            self.post_one(post)
        except Exception as e:
            self.logger.error(e)

    def post_one(self, post: Post):
        if post.type == 'link':
            lines = [
                post.title,
                post.url,
                # post.comments,
                '#' + post.subreddit + ' ' + post.comments
            ]
            caption = '\n'.join(lines)
            self.bot.send_message(text=caption,
                                  chat_id=self.channel_id,
                                  timeout=self.timeout)
        else:
            title = self.cut_text(post.title, limit=MAX_CAPTION_LENGTH-len(post.subreddit)-len(post.comments)-5)
            caption = title + '\n' + '#' + post.subreddit + ' ' + post.comments
            kwargs = {
                'caption': caption,
                'chat_id': self.channel_id,
                'timeout': self.timeout,
            }
            if post.type == 'photo':
                self.bot.send_photo(photo=post.url, **kwargs)
            elif post.type == 'video':
                self.bot.send_video(video=post.url, **kwargs)

    def cut_text(self, text: str, limit=MAX_CAPTION_LENGTH):
        if text is None:
            return ''
        elif len(text) > limit:
            text = text[:limit - 5]
            without_last = text.split()[:-1]
            text = ' '.join(without_last)
            return text + '...'
        else:
            return text
