import logging
import traceback
from typing import Any

import telegram
from telegram import Bot
from telegram.error import TimedOut, BadRequest, TelegramError
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH

from settings import POST_TIMEOUT, CHANNEL_ID
from src.post import Post
from src.image import Image


logger = logging.getLogger('🗞 ' + __name__)


def publish_post(bot, post: Post, db):
    logger.info(post)
    success = exceptions_handler_wrapper(publish_title, bot, post)(bot, post)

    if not success:
        return
    else:
        db.add(post)

    for image in post.images:
        logger.info(f'    | {image}')
        exceptions_handler_wrapper(publish_item, bot, image)(bot, image, post.is_album)


def exceptions_handler_wrapper(f, bot, obj: Post or Image):
    def decorated(*args, **kwargs):
        counter = 0
        while counter < 1:
            # success = exceptions_handler_wrapper(publish_item, post)(bot, image)
            success = False
            try:
                success = f(*args, **kwargs)
            except TimedOut as e:
                log_error('TimedOut', e, obj, bot)
            except BadRequest as e:
                log_error('BadRequest', e, obj, bot)
            except TelegramError as e:
                log_error('TelegramError', e, obj, bot, print_traceback=True)
            except Exception as e:
                log_error('Something horrible', e, obj, bot, print_traceback=True)
            if success:
                return True
            else:
                counter += 1
        return False

    return decorated


def log_error(title: str, err, obj: Post or Image, bot: telegram.Bot,
              print_traceback=False,
              print_post=True):
    logger.error(title)
    logger.error(err)
    if print_traceback:
        for line in traceback.format_exc().split('\n'):
            logger.error(line)
    if print_post:
        logger.error(f'🚨 {obj}')
    if type(obj) is Image:
        bot.send_message(chat_id=CHANNEL_ID,
                         text='< missed image >',
                         disable_web_page_preview=True,
                         timeout=POST_TIMEOUT)


def publish_title(bot, post: Post):
    text = format_title(post)
    bot.send_message(chat_id=CHANNEL_ID,
                     text=text,
                     disable_web_page_preview=True,
                     timeout=POST_TIMEOUT)
    return True


def publish_item(bot: Bot, image: Image, is_album):
    text = format_image_caption(image, is_album)

    kwargs = {
        'caption': text,
        'chat_id': CHANNEL_ID,
        'disable_notification': True,
        'timeout': POST_TIMEOUT,
    }

    if image.animated:
        bot.send_video(video=image.src, **kwargs)
    else:
        bot.send_photo(photo=image.src, **kwargs)
    return True


def format_title(post):
    strings = ['🌚 ' + butch for butch in post.title.split('\n')]
    if post.is_dump:
        strings.append(f'🔥 Album with {post.images_count} items')
    strings.append('🔗 ' + post.link)
    if post.tags:
        strings.append('🏷 ' + ' '.join(post.tags))
    if not post.is_album and post.desc:
        strings.append(post.desc)
    text = '\n'.join(strings)
    return cut_text(text, limit=MAX_CAPTION_LENGTH * 2)


def format_image_caption(image: Image, is_album: bool):
    if is_album:
        return cut_text(image.desc, limit=MAX_CAPTION_LENGTH)
    else:
        return ''


def cut_text(text: str, limit):
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
