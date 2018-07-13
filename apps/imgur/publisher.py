import logging
from time import sleep
from typing import List

from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, TelegramError

from memes_reposter.telegram_bot import bot
from .models import ImgurConfig, Media, Post


logger = logging.getLogger(__name__)


def publish_posts(posts: List[Post], config: ImgurConfig):
    size = len(posts)
    for i, post in enumerate(posts):
        published = publish_post(post, config)
        sleep(0.5)
        if published:
            logger.info('Published %3d/%d: %s', i + 1, size, repr(post))
        post.save()


def publish_blank(posts: List[Post]):
    for post in posts:
        logger.info('Blank publishing: %s', repr(post))
        post.save()


def publish_post(post: Post, config: ImgurConfig):
    delete_on_fail = settings.IMGUR_DELETE_ON_FAIL
    try:
        if post.is_single:
            publish_single(post, config)
        else:
            publish_album(post, config, delete_on_fail)
        return True
    except TelegramError as e:
        logger.exception('Error %s: %s for post %s', type(e), e, repr(post))
        return False


def send_media(chat_id, media: Media, caption=None, reply_markup=None):
    common = dict(chat_id=chat_id, caption=caption, reply_markup=reply_markup)
    if media.animated:
        return bot.send_video(video=media.link, **common)
    else:
        return bot.send_photo(photo=media.link, **common)


def get_media_input(media: Media, caption=None):
    if media.animated:
        inp = InputMediaVideo(media.link, caption=caption)
    else:
        inp = InputMediaPhoto(media.link, caption=caption)
    return inp


def format_album_title(post: Post):
    title = post.title.strip()
    if post.images_count > len(post.medias):
        title = f"🔥 Album [ {post.images_count} ]\n" + title
    title += f"\n{post.link}"
    return title


def post_title(post: Post, config: ImgurConfig):
    title = format_album_title(post)
    # reply_markup = build_keyboard_markup(post)
    title_message = bot.send_message(
        chat_id=config.chat_id, text=title,
        # reply_markup=reply_markup,
        disable_web_page_preview=True)
    return title_message


def publish_single(post: Post, config: ImgurConfig):
    title_message = post_title(post, config)
    try:
        media = post.medias[0]
        send_media(config.chat_id, media)
    except TelegramError as e:
        logger.exception('Error %s: %s for post %s', type(e), e, repr(post))
        title_message.delete()


def publish_album(post: Post, config: ImgurConfig, delete_on_fail=True):
    title_message = post_title(post, config)
    medias = [
        get_media_input(media)
        for media in post.medias[:10]
    ]
    try:
        bot.send_media_group(media=medias, chat_id=config.chat_id)
    except TelegramError as e:
        logger.exception('Error %s: %s for post %s', type(e), e, repr(post))
        if delete_on_fail:
            title_message.delete()


def build_keyboard_markup(post: Post):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('comments', url=post.link + '#comments-container'),
        InlineKeyboardButton('post', url=post.link),
    ]])
