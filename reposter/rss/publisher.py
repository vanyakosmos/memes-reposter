import html
from typing import Optional

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, MAX_CAPTION_LENGTH, ParseMode

from .models import Channel, Post


def short_link(link: str):
    # todo: generate short link
    return link


def format_message(channel: Channel, post: Post):
    link = post.link
    title = html.escape(post.title)
    if channel.short_link:
        link = short_link(link)

    if channel.linked_title:
        msg = f'<a href="{link}">{title}</a>'
        length = len(title)
    else:
        msg = f'{title}\n{link}'
        length = len(msg)

    if channel.signature:
        signature = f'\n\n{channel.signature}'
        msg += signature
        length += len(signature)
    return msg, length


def post_exists(channel: Channel, post: Post):
    return Post.objects.filter(link=post.link, feed__channel=channel).exists()


def build_keyboard(post: Post, buttons_type: str):
    if buttons_type == Channel.NO_BUTTONS:
        return None
    keyboard = []
    if buttons_type == Channel.LINK_AND_COMMENTS_BUTTONS and post.comments_link:
        keyboard.append(InlineKeyboardButton('comments', url=post.comments_link))
    if buttons_type in (Channel.LINK_BUTTON, Channel.LINK_AND_COMMENTS_BUTTONS):
        keyboard.append(InlineKeyboardButton('read', url=post.link))

    if not keyboard:
        return None
    return InlineKeyboardMarkup([
        keyboard
    ])


def publish_with_picture(bot: Bot, post: Post, message: str, length: int,
                         keyboard: Optional[InlineKeyboardMarkup],
                         config: dict):
    if length > MAX_CAPTION_LENGTH:
        bot.send_photo(photo=post.pic_link, **config)
        bot.send_message(text=message, reply_markup=keyboard, **config)
    else:
        bot.send_photo(photo=post.pic_link, caption=message, reply_markup=keyboard, **config)


def publish_post(bot: Bot, channel: Channel, post: Post):
    message, length = format_message(channel, post)
    if post_exists(channel, post):
        return False
    post.save()  # fast save before actual posting
    keyboard = build_keyboard(post, channel.buttons_type)
    config = {
        'chat_id': channel.chat_id,
        'parse_mode': ParseMode.HTML,
    }
    if post.pic_link and channel.publish_picture:
        config['disable_web_page_preview'] = True
        publish_with_picture(bot, post, message, length, keyboard, config)
    else:
        bot.send_message(text=message, reply_markup=keyboard, **config)
    return True
