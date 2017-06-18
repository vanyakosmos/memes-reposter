import traceback

from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH
from telegram.error import TimedOut, BadRequest, TelegramError

from autoposter import AbstractPublisher
from settings import POST_TIMEOUT
from .wrappers import Image, Post


class ImgurPostPublisher(AbstractPublisher):
    def publish(self, post):
        self.logger.debug(post)
        success = self.exceptions_handler_wrapper(self.publish_title, post)(post)

        if not success:
            return
        else:
            self.db.add(post)

        for image in post.images:
            self.logger.debug(f'    | {image}')
            self.exceptions_handler_wrapper(self.publish_item, image)(image, post)

    def exceptions_handler_wrapper(self, f, obj):
        def decorated(*args, **kwargs):
            counter = 0
            while counter < 1:
                # success = exceptions_handler_wrapper(publish_item, post)(bot, image)
                success = False
                try:
                    success = f(*args, **kwargs)
                except (TimedOut, BadRequest) as e:
                    self.log_error(e, obj)
                except (TelegramError, Exception) as e:
                    self.log_error(e, obj, print_traceback=True)
                if success:
                    return True
                else:
                    counter += 1
            return False

        return decorated

    def log_error(self, err: Exception, obj,
                  print_traceback=False,
                  print_post=True):
        self.logger.error(err.__class__.__name__)
        self.logger.error(err)
        if print_traceback:
            for line in traceback.format_exc().split('\n'):
                self.logger.error(line)
        if print_post:
            self.logger.error(obj)

    def publish_title(self, post: Post):
        text = self.format_title(post)
        self.bot.send_message(chat_id=self.channel_id,
                              text=text,
                              disable_web_page_preview=True,
                              timeout=POST_TIMEOUT)
        return True

    def publish_item(self, image: Image, post: Post):
        is_single_image = post.images_count == 1
        text = self.format_image_caption(image, is_single_image)

        kwargs = {
            'caption': text,
            'chat_id': self.channel_id,
            'disable_notification': True,
            'timeout': POST_TIMEOUT,
        }

        if image.animated:
            self.bot.send_video(video=image.src, **kwargs)
        else:
            self.bot.send_photo(photo=image.src, **kwargs)
        return True

    @staticmethod
    def format_title(post):
        strings = ['🌚 ' + butch for butch in post.title.split('\n')]
        if post.is_dump:
            strings.append(f'🔥 Album with {post.images_count} items')
        strings.append('🔗 ' + post.link)
        if post.tags:
            strings.append('🏷 ' + ' '.join(post.tags))
        if post.images_count == 1 and post.desc:
            strings.append(post.desc)
        text = '\n'.join(strings)
        return ImgurPostPublisher.cut_text(text, limit=MAX_MESSAGE_LENGTH)

    @staticmethod
    def format_image_caption(image: Image, is_single_image: bool):
        if not is_single_image:
            return ImgurPostPublisher.cut_text(image.desc, limit=MAX_CAPTION_LENGTH)
        else:
            return ''

    @staticmethod
    def cut_text(text: str, limit: int):
        limit -= 10
        if text is None:
            return ''
        elif len(text) > limit:
            text = text[:limit - 5]
            cut = text.split()[:-1]
            text = ' '.join(cut)
            return text + '...'
        else:
            return text
