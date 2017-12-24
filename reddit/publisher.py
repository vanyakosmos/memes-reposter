import html

from telegram import MAX_CAPTION_LENGTH, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater

from core.publisher import BasePublisher
from .store import RedditStore
from .models import Post


class RedditPublisher(BasePublisher):
    def __init__(self, channel_id: str, updater: Updater, store: RedditStore):
        super().__init__(channel_id, updater)
        self.store = store
        self.timeout = 60  # seconds

    def publish(self, post: Post, *args, **kwargs):
        self.store.save_post(post)
        self.logger.info('Posting: ' + str(post))

        try:
            self.post_one(post)
        except Exception as e:
            self.logger.error(e)

    def build_keyboard_markup(self, post: Post, pass_original=True):
        row = []
        if pass_original:
            row.append(InlineKeyboardButton('original', url=post.url))
        row.append(InlineKeyboardButton('comments', url=post.comments))
        row.append(InlineKeyboardButton('👏', callback_data=f'{post.id}:clap'))
        return InlineKeyboardMarkup([row])

    def post_one(self, post: Post):
        if post.type in ('text', 'link'):

            title = html.escape(post.title)
            title = f'{title}\n'
            if post.type == 'link':
                text = title + f'{post.url}'
            else:
                text = title + f'{post.url}'  # fixme: post.text

            keyboard_markup = self.build_keyboard_markup(post, pass_original=False)
            self.bot.send_message(text=text,
                                  chat_id=self.channel_id,
                                  reply_markup=keyboard_markup,
                                  parse_mode=ParseMode.HTML,
                                  timeout=self.timeout)
        else:
            keyboard_markup = self.build_keyboard_markup(post)
            kwargs = {
                'caption': self.cut_text(post.title),
                'chat_id': self.channel_id,
                'timeout': self.timeout,
                'reply_markup': keyboard_markup,
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
