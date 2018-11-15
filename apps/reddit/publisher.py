import html
import logging
import re
from time import sleep
from typing import List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, \
    MAX_CAPTION_LENGTH, ParseMode, TelegramError

from memes_reposter.telegram_bot import bot
from .models import Post


logger = logging.getLogger(__name__)
REPOST_REGEX = re.compile(r'\(\s*(x-?|re)post .+\)')


def publish_posts(posts: List[Post]):
    size = len(posts)
    for i, post in enumerate(posts):
        post.save()
        if post.status != Post.STATUS_ACCEPTED:
            logger.info('Skipped %3d/%d: %s', i + 1, size, repr(post))
            continue
        published = publish_post(post)
        sleep(0.5)
        if published:
            logger.info('Published %3d/%d: %s', i + 1, size, repr(post))
        else:
            logger.info('Error %3d/%d: %s', i + 1, size, repr(post))


def publish_blank(posts: List[Post]):
    for post in posts:
        logger.info('Blank publishing: %s', repr(post))
        post.save()


def publish_post(post: Post, post_title=None):
    chat_id = post.subreddit.channel.chat_id
    try:
        if post.is_not_media():
            publish_post_link(post, chat_id)
        else:
            publish_media_post(post, chat_id, post_title)
        return True
    except TelegramError as e:
        logger.error('Error %s: %s for post %s', type(e), e, repr(post))
        return False


def format_title(post: Post, escape=False) -> Optional[str]:
    title = post.title
    title = REPOST_REGEX.sub('', title).strip()
    if escape:
        title = html.escape(title)
    if not title:
        return
    return title


def publish_post_link(post: Post, channel_id: str):
    title = format_title(post)
    text = title + f'\n{post.link}'

    keyboard_markup = build_keyboard_markup(post, pass_original=False)
    bot.send_message(text=text,
                     chat_id=channel_id,
                     reply_markup=keyboard_markup,
                     parse_mode=ParseMode.HTML)


def publish_media_post(post: Post, channel_id: str, post_title=None):
    title = format_title(post)
    keyboard_markup = build_keyboard_markup(post)
    common = {
        'chat_id': channel_id,
        'reply_markup': keyboard_markup,
    }
    subreddit = post.subreddit
    show_title = subreddit.show_title if post_title is None else post_title
    # need title, post pic and text separately
    if show_title and title and len(title) > MAX_CAPTION_LENGTH:
        publish_media(post, chat_id=channel_id)
        kwargs = dict(text=title, **common)
        bot.send_message(**kwargs)
    # need title, post pic with caption
    elif show_title:
        kwargs = dict(caption=title, **common)
        publish_media(post, **kwargs)
    # post just pic
    else:
        kwargs = dict(**common)
        publish_media(post, **kwargs)


def publish_media(post: Post, **kwargs):
    if post.media_type == Post.MEDIA_PHOTO:
        bot.send_photo(photo=post.media_link, **kwargs)
    elif post.media_type == Post.MEDIA_VIDEO:
        try:
            bot.send_video(video=open(post.file_path, 'rb'), **kwargs)
        except Exception as e:
            logger.error(e)
            bot.send_video(video=post.media_link, **kwargs)


def build_keyboard_markup(post: Post, pass_original=True):
    keyboard = []
    if pass_original:
        keyboard.append(InlineKeyboardButton('original', url=post.media_link))
    keyboard.append(InlineKeyboardButton('comments', url=post.comments_full))

    return InlineKeyboardMarkup([
        keyboard,
    ])
