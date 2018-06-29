import html
import logging
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MAX_CAPTION_LENGTH, ParseMode, TelegramError

from memes_reposter.telegram_bot import bot
from .models import Post, Subreddit


logger = logging.getLogger(__name__)


def publish_posts(posts: List[Post], subreddit: Subreddit, blank=False):
    for post in posts:
        if blank:
            logger.info('Blank publishing: %s', repr(post))
        else:
            published = publish_post(post, subreddit)
            if published:
                logger.info('Publishing: %s', repr(post))
        post.save()


def publish_post(post: Post, subreddit: Subreddit):
    channel_id = subreddit.channel.name
    try:
        if post.meta.type in ('text', 'link'):
            publish_post_link(post, channel_id)
        else:
            publish_media_post(post, channel_id, subreddit)
        return True
    except TelegramError as e:
        logger.error('Error %s: %s for post %s', type(e), e, repr(post))
        return False


def publish_post_link(post: Post, channel_id: str):
    title = html.escape(post.title)
    title = f'{title}\n'
    text = title + f'{post.link}'

    keyboard_markup = build_keyboard_markup(post, pass_original=False)
    bot.send_message(text=text,
                     chat_id=channel_id,
                     reply_markup=keyboard_markup,
                     parse_mode=ParseMode.HTML)


def publish_media_post(post: Post, channel_id: str, subreddit: Subreddit):
    keyboard_markup = build_keyboard_markup(post)
    common = {
        'chat_id': channel_id,
        'reply_markup': keyboard_markup,
    }
    # need title, post pic and text separately
    if subreddit.show_title and len(post.title) > MAX_CAPTION_LENGTH:
        publish_media(post, chat_id=channel_id)
        kwargs = dict(text=post.title, **common)
        bot.send_message(**kwargs)
    # need title, post pic with caption
    elif subreddit.show_title:
        kwargs = dict(caption=post.title, **common)
        publish_media(post, **kwargs)
    # post just pic
    else:
        kwargs = dict(**common)
        publish_media(post, **kwargs)


def publish_media(post: Post, **kwargs):
    if post.meta.type == 'photo':
        bot.send_photo(photo=post.meta.media_link, **kwargs)
    elif post.meta.type == 'video':
        bot.send_video(video=post.meta.media_link, **kwargs)


def build_keyboard_markup(post: Post, pass_original=True):
    keyboard = []
    if pass_original:
        keyboard.append(InlineKeyboardButton('original', url=post.meta.media_link))
    keyboard.append(InlineKeyboardButton('comments', url=post.comments_full))

    return InlineKeyboardMarkup([
        keyboard,
    ])
