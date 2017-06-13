import logging
import time
from pprint import pformat

import telegram
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH


def publish_posts(bot: telegram.Bot, channel_id, posts: list):
    logging.info(f'Publishing {len(posts)} post(s) into telegram')
    for i, post in enumerate(posts[:20]):
        try:
            logging.info(f'\t> #{i+1:3d} : {post["title"]}')
            publish_post_title(bot, channel_id, post)
            time.sleep(2)

            for image in post['images']:
                publish_post_image(bot, channel_id, image, post)
                time.sleep(2)

        except telegram.error.TimedOut:
            logging.error(f'Timeout error ⌛ (bad connection? dunno)️\n'
                          f'{pformat(post)}')


def publish_posts_guarded(bot: telegram.Bot, channel_id, posts: list, db):
    logging.info(f'Publishing {len(posts)} post(s) into telegram')
    for i, post in enumerate(posts):
        db.add(post)

        logging.info(f'Database items:     {len(db):4d}')
        logging.info(f'Current chunk size: {len(posts):4d}')
        logging.info(f'\t> #{i+1:3d} : {post["title"]}')
        try_to_publish(bot, channel_id, post, publish_post_title)

        for image in post['images']:
            logging.info(f'\t\t> : {image["src"]}')
            try_to_publish(bot, channel_id, image, publish_post_image)

        time.sleep(30)


def try_to_publish(bot, channel_id, item, publisher_callback):
    timeout = 120
    try:
        publisher_callback(bot, channel_id, item, timeout)
    except telegram.error.TimedOut as e:
        logging.error(f'TimeOut: ⌛ > {timeout}s')
        logging.error(e)
        for line in pformat(item).split('\n'):
            logging.error(line)
    except telegram.error.BadRequest as e:
        logging.error('BadRequest')
        logging.error(e)
        for line in pformat(item).split('\n'):
            logging.error(line)
    except telegram.error.TelegramError as e:
        logging.error('TelegramError')
        logging.error(e)
        for line in pformat(item).split('\n'):
            logging.error(line)


def publish_post_title(bot, channel_id, post, timeout):
    title = post["title"]
    # desc = post['desc']
    # topic = '#' + '_'.join(post["topic"].split())
    tags = ' '.join(post["tags"])
    link = post["link"]

    strings = ['🌚 ' + butch for butch in title.split('\n')]
    if post['is_dump']:
        images_count = post["images_count"]
        strings.append(f'🔥 Album with {images_count} items')
    strings.append('🔗 ' + link)
    if tags:
        strings.append('🏷 ' + tags)

    text = '\n'.join(strings)
    text = cut_text(text, limit=MAX_MESSAGE_LENGTH)

    bot.send_message(chat_id=channel_id,
                     text=text,
                     disable_web_page_preview=True,
                     timeout=timeout)


def publish_post_image(bot, channel_id, image, timeout):
    is_album = image['is_album']
    animated = image['animated']
    title = image['title']
    desc = image['desc']
    src = image['src']

    text = ''

    if is_album and title:
        text += title + '\n'
    if desc:
        text += desc
    text = cut_text(text, limit=MAX_CAPTION_LENGTH)

    kwargs = {
        'caption': text,
        'chat_id': channel_id,
        'disable_notification': True,
        'timeout': timeout,

    }

    if animated:
        bot.send_video(video=src, **kwargs)
    else:
        bot.send_photo(photo=src, **kwargs)


def cut_text(text: str, limit=200):
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
