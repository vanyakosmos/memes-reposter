import logging

from telegram.error import BadRequest, TelegramError
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH

from settings import POST_TIMEOUT, CHANNEL_ID


logger = logging.getLogger(__name__)


def publish_post(bot, post, db):
    try:
        db.add(post)
        logger.info(f'Post: {post["link"]}')
        publish_title(bot, post)

        for image in post['images']:
            logger.info(f'    | Item: {image["src"]}')
            publish_item(bot, image)
    except BadRequest as e:
        logger.error('BadRequest')
        logger.error(e)
    except TelegramError as e:
        logger.error('TelegramError')
        logger.error(e)


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
