import html
import logging
import re
from typing import Optional

from telegram import (
    TelegramError,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    MAX_CAPTION_LENGTH,
    ParseMode,
)

from .bot import bot
from core.post import Post

logger = logging.getLogger(__name__)
REPOST_REGEX = re.compile(r'\(\s*(x-?|re)post .+\)')

Chat = 'telegram_app.models.Chat'


def publish_post(chat: Chat, post: Post):
    try:
        if post.text:
            publish_text(chat, post)
            return True
        if post.photo_url or post.video_url:
            publish_media_post(chat, post)
            return True
        if post.url:
            publish_post_link(chat, post)
            return True
        return False
    except TelegramError as e:
        logger.error('Error %s: %s for post %s', type(e), e, repr(post))
        return False


def format_title(post: Post, escape=False) -> Optional[str]:
    title = post.title or ''
    title = REPOST_REGEX.sub('', title).strip()
    if escape:
        title = html.escape(title)
    return title


def publish_text(chat: Chat, post: Post):
    text = post.text
    title = format_title(post)
    if title:
        text = f'*{title}*\n\n{text}'

    keyboard_markup = build_keyboard_markup(post, pass_original=False)
    bot.send_message(
        text=text,
        chat_id=chat.telegram_id,
        reply_markup=keyboard_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


def publish_post_link(chat: Chat, post: Post):
    text = post.url
    title = format_title(post)
    if title:
        text = title + f'\n{text}'

    keyboard_markup = build_keyboard_markup(post, pass_original=False)
    bot.send_message(
        text=text,
        chat_id=chat.telegram_id,
        reply_markup=keyboard_markup,
        parse_mode=ParseMode.HTML,
    )


def publish_media_post(chat: Chat, post: Post):
    title = format_title(post)
    keyboard_markup = build_keyboard_markup(post)
    common = {
        'chat_id': chat.telegram_id,
        'reply_markup': keyboard_markup,
    }
    # need title, post pic and text separately
    if title and len(title) > MAX_CAPTION_LENGTH:
        publish_media(post, chat_id=chat.telegram_id)
        kwargs = dict(text=title, **common)
        bot.send_message(**kwargs)
    # need title, post pic with caption
    elif title:
        kwargs = dict(caption=title, **common)
        publish_media(post, **kwargs)
    # post just pic
    else:
        kwargs = dict(**common)
        publish_media(post, **kwargs)


def publish_media(post: Post, **kwargs):
    if post.photo_url:
        bot.send_photo(photo=post.photo_url, **kwargs)
    elif post.video_url:
        if post.file_path:
            with open(post.file_path, 'rb') as f:
                bot.send_video(video=f, **kwargs)
        else:
            bot.send_video(video=post.video_url, **kwargs)


def build_keyboard_markup(post: Post, pass_original=True):
    keyboard = []
    url = post.photo_url or post.url
    if pass_original and url:
        keyboard.append(InlineKeyboardButton('original', url=url))
    if post.comments:
        keyboard.append(InlineKeyboardButton('comments', url=post.comments))

    if not keyboard:
        return
    return InlineKeyboardMarkup([keyboard])
