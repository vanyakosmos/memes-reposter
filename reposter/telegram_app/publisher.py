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
            return publish_text(chat, post)
        if post.photo_url or post.video_url:
            return publish_media_post(chat, post)
        if post.url:
            return publish_post_link(chat, post)
    except TelegramError as e:
        logger.error('Error %s: %s', type(e), e)


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
    return bot.send_message(
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
    return bot.send_message(
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
        msg = publish_media(post, chat_id=chat.telegram_id)
        if msg:
            return bot.send_message(text=title, reply_to_message_id=msg.message_id, **common)
        return
    # need title, post pic with caption
    if title:
        return publish_media(post, caption=title, **common)
    # post just pic
    return publish_media(post, **common)


def publish_media(post: Post, **kwargs):
    if post.photo_url:
        return bot.send_photo(photo=post.photo_url, **kwargs)
    if post.video_url:
        if post.file_path:
            with open(post.file_path, 'rb') as f:
                return bot.send_video(video=f, **kwargs)
        else:
            return bot.send_video(video=post.video_url, **kwargs)


def build_keyboard_markup(post: Post, pass_original=True):
    keyboard = []
    url = post.photo_url or post.url
    if pass_original and url and not post.video_url:
        keyboard.append(InlineKeyboardButton('open', url=url))
    if post.comments:
        keyboard.append(InlineKeyboardButton('comments', url=post.comments))

    if not keyboard:
        return
    return InlineKeyboardMarkup([keyboard])
