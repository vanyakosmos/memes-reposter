import logging
import traceback
from pprint import pformat

from telegram.error import TimedOut, BadRequest, TelegramError
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH

from settings import POST_TIMEOUT, CHANNEL_ID


logger = logging.getLogger('🗞 ' + __name__)


def publish_post(bot, post, db):
    try:
        db.add(post)
        logger.info(f'Post: {post["title"][:40]}')
        logger.info(f'    : {post["link"]}')
        publish_title(bot, post)

        for image in post['images']:
            logger.info(f'    | Item: {image["src"]}')
            publish_item(bot, image)
    except TimedOut as e:
        log_error('TimedOut', e, post)
    except BadRequest as e:
        log_error('BadRequest', e, post)
    except TelegramError as e:
        log_error('TelegramError', e, post, print_traceback=True)
    except Exception as e:
        log_error('Something horrible', e, post, print_traceback=True)


def log_error(title: str, err, post,
              print_traceback=False,
              print_post=True):
    logger.error(title)
    logger.error(err)
    if print_traceback:
        for line in traceback.format_exc().split('\n'):
            logger.error(line)
    if print_post:
        for line in pformat(post).split('\n'):
            logger.error(line)


def publish_title(bot, post):
    text = format_title(post['title'], post['link'], post['tags'],
                        post['is_dump'], post['images_count'])
    bot.send_message(chat_id=CHANNEL_ID,
                     text=text,
                     disable_web_page_preview=True,
                     timeout=POST_TIMEOUT)


def publish_item(bot, image):
    animated = image['animated']
    src = image['src']

    text = format_image_caption(image['title'], image['desc'],
                                image['is_album'])

    kwargs = {
        'caption': text,
        'chat_id': CHANNEL_ID,
        'disable_notification': True,
        'timeout': POST_TIMEOUT,
    }

    if animated:
        bot.send_video(video=src, **kwargs)
    else:
        bot.send_photo(photo=src, **kwargs)


def format_title(title, link, tags, is_dump, images_count):
    strings = ['🌚 ' + butch for butch in title.split('\n')]
    if is_dump:
        strings.append(f'🔥 Album with {images_count} items')
    strings.append('🔗 ' + link)
    if tags:
        strings.append('🏷 ' + ' '.join(tags))

    text = '\n'.join(strings)
    return cut_text(text, limit=MAX_MESSAGE_LENGTH)


def format_image_caption(title, desc, is_album):
    text = ''
    if is_album and title:
        text += title + '\n'
    if desc:
        text += desc
    return cut_text(text, limit=MAX_CAPTION_LENGTH)


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
