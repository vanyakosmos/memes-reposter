from telegram import InputMediaPhoto, InputMediaVideo, MAX_CAPTION_LENGTH, Message
from telegram.ext import Updater

from core.publisher import BasePublisher
from core.store import IdStore
from .models import Image, Post


class ImgurPublisher(BasePublisher):
    def __init__(self, channel_id: str, updater: Updater, store: IdStore):
        super().__init__(channel_id, updater)
        self.store = store
        self.timeout = 60
        self.messages = []

    def publish(self, post: Post, *args, **kwargs):
        self.store.save_id(post.id)
        self.logger.info('Posting: ' + str(post))
        self.messages = []

        try:
            self.post_album(post)
        except Exception as e:
            self.logger.error(e)
            self.logger.info(f'Deleting post: {post}')
            for msg in self.messages:
                self.logger.info(f'Deleting msg: {msg.message_id}')
                msg.delete()

    def post_album(self, post: Post):
        msg = self.post_title(post)
        self.messages.append(msg)

        if len(post.images) == 1:
            image = post.images[0]
            msg = self.post_image(image, post.is_album)
            self.messages.append(msg)
            return

        media = [
            self.get_media_input(image)
            for image in post.images[:10]
        ]

        self.bot.send_media_group(media=media,
                                  chat_id=self.channel_id,
                                  timeout=self.timeout * len(media))

    def post_title(self, post: Post) -> Message:
        text = self.format_header(post)
        return self.bot.send_message(chat_id=self.channel_id,
                                     text=text,
                                     disable_web_page_preview=True,
                                     timeout=self.timeout)

    def get_media_input(self, image: Image):
        caption = self.format_caption(image)
        if image.animated:
            inp = InputMediaVideo(image.url, caption=caption)
        else:
            inp = InputMediaPhoto(image.url, caption=caption)
        return inp

    def post_image(self, image: Image, is_album) -> Message:
        text = self.format_caption(image) if is_album else ''
        kwargs = {
            'caption': text,
            'chat_id': self.channel_id,
            'disable_notification': True,
            'timeout': self.timeout,
        }
        if image.animated:
            return self.bot.send_video(video=image.url, **kwargs)
        else:
            return self.bot.send_photo(photo=image.url, **kwargs)

    def format_header(self, post: Post):
        strings = []
        if post.is_long:
            strings.append(f'🔥 Album [ {post.size} ]')
        strings.append(post.title.strip())
        strings.append(post.url)
        if post.desc:
            strings.append(post.desc)
        text = '\n'.join(strings)
        return self.cut_text(text, limit=400)

    def format_caption(self, image: Image):
        return self.cut_text(image.desc, limit=MAX_CAPTION_LENGTH)

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
