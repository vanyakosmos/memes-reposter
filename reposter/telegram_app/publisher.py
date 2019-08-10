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
    InputMediaVideo,
    InputMediaPhoto,
)

from .bot import bot
from core.post import Post, Media

logger = logging.getLogger(__name__)
REPOST_REGEX = re.compile(r'\(\s*(x-?|re)post .+\)')

Chat = 'telegram_app.models.Chat'


def publish_post(chat: Chat, post: Post):
    try:
        if post.text:
            return publish_text(chat, post)
        if post.medias:
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

    keyboard_markup = build_keyboard_markup(post)
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

    keyboard_markup = build_keyboard_markup(post)
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
    if title and len(title) > MAX_CAPTION_LENGTH or len(post.medias) > 1:
        messages = publish_media(post, chat_id=chat.telegram_id)
        if messages:
            return bot.send_message(
                text=title,
                reply_to_message_id=messages[0].message_id,
                **common,
            )
        return
    # need title, post pic with caption
    if title:
        return publish_media(post, caption=title, **common)
    # post just pic
    return publish_media(post, **common)


def get_media_input(media: Media):
    Input = InputMediaPhoto
    if media.video:
        Input = InputMediaVideo
    return Input(media.url, caption=media.caption)


def publish_media(post: Post, **kwargs):
    # post album
    if len(post.medias) > 1:
        medias = [get_media_input(m) for m in post.medias[:10]]
        return bot.send_media_group(media=medias, **kwargs)

    if len(post.medias) == 1:
        media = post.medias[0]
        # post video using url or local file
        if media.video:
            if media.file_path:
                with open(media.file_path, 'rb') as f:
                    return bot.send_video(video=f, **kwargs)
            else:
                return bot.send_video(video=media.url, **kwargs)
        # post photo
        return bot.send_photo(photo=media.url, **kwargs)


def build_keyboard_markup(post: Post):
    keyboard = []
    if post.url and post.url != post.comments:
        keyboard.append(InlineKeyboardButton('link', url=post.url))
    if post.comments:
        keyboard.append(InlineKeyboardButton('comments', url=post.comments))

    if not keyboard:
        return
    return InlineKeyboardMarkup([keyboard])
