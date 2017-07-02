from typing import List
import re

from telegram import MAX_FILESIZE_DOWNLOAD

from autoposter import AbstractFilter, AbstractDB
from settings import BANNED_TAGS, IMAGES_FOR_LONG_POST, IMAGES_PER_POST
from settings import MAX_VIDEO_SIZE, MAX_IMAGE_SIZE, MIN_DIM_RATIO

from .fetcher import AlbumFetcher
from .wrappers import Post, Image, RedditPost


class ImageValidatorMixin(object):
    @staticmethod
    def valid_image(image: Image) -> bool:
        if image.size == 0:
            return False

        normal_image_size = image.animated or image.size < MAX_IMAGE_SIZE
        normal_size = image.size < MAX_VIDEO_SIZE
        large_size = not normal_size and image.size < MAX_FILESIZE_DOWNLOAD
        good_ration = image.width / image.height > MIN_DIM_RATIO and image.height / image.width > MIN_DIM_RATIO

        return normal_image_size and (normal_size or large_size) and good_ration


class PostsFilter(AbstractFilter, ImageValidatorMixin):
    def __init__(self, db: AbstractDB):
        super().__init__(db)
        self.album_fetcher = AlbumFetcher()

    def filter(self, posts) -> List[Post]:
        """
        Args:
            posts (List[dict]): Posts obtained from Imgur gallery.

        Returns:
            List[Post]: list of Post objects.
        """
        filtered_posts = []
        posts_ids = self.db.keys()

        for post_dict in posts:
            post = Post(post_dict)

            if post.id in posts_ids:
                continue

            for tag in post.tags:
                if tag in BANNED_TAGS:
                    continue

            post.is_dump = post.images_count > IMAGES_PER_POST
            images = self.filtrate_images(images_list=post_dict.get('images', []),
                                          post=post)
            if images:
                post.images = images
                filtered_posts.append(post)

        return filtered_posts

    def filtrate_images(self, images_list: List[dict], post: Post) -> List[Image]:
        if post.is_album:
            if post.images_count <= 3:
                return self.collect_images(images_list, 3)

            response = self.album_fetcher.fetch(post.id)
            if response.success:
                album = response.data
                limit = IMAGES_FOR_LONG_POST if post.is_dump else IMAGES_PER_POST
                return self.collect_images(album, limit)
        else:
            image = Image(post.post_dict)
            if self.valid_image(image):
                return [image]
        return []

    def collect_images(self, images: List[dict], limit: int) -> List[Image]:
        picked_images = []
        for image_dict in images:
            if len(picked_images) >= limit:
                break
            image = Image(image_dict)
            if self.valid_image(image):
                picked_images.append(image)
        return picked_images


class RedditFilter(AbstractFilter):
    def __init__(self, db: AbstractDB, subreddit: str, score: int):
        super().__init__(db)
        self.score = score
        self.subreddit = subreddit

    def filter(self, posts: List[dict]) -> List[Post]:
        """
        Args:
            posts (List[dict]): Posts obtained from Imgur gallery.

        Returns:
            List[Post]: list of Post objects.
        """
        filtered_posts = []
        posts_ids = self.db.keys()

        for post_dict in posts:
            post = post_dict['data']

            if post['id'] in posts_ids:
                continue

            if post['score'] < self.score:
                break  # assumed that posts sorted by score in descending order

            filtered_post = self._map_post(post)
            filtered_posts.append(filtered_post)

        return filtered_posts

    @staticmethod
    def _has_ext(file: str, *exts):
        return any([file.endswith(ext) for ext in exts])

    def _map_post(self, post):
        self.logger.debug('Domain:  ' + post['domain'])
        self.logger.debug('Url:     ' + post['url'])
        comments = "https://redd.it/" + post['id']
        post['url'] = re.sub(r'(.+)\?.+', '\g<1>', post['url'])
        if self._has_ext(post['url'], '.png', '.jpg'):
            typ = 'photo'
        elif self._has_ext(post['url'], '.gif', '.gifv'):
            typ = 'video'
            if self._has_ext(post['url'], '.gifv') and re.match(r'(i.)?imgur.com', post['domain']):
                post['url'] = re.sub(r'^(.+)\.gifv?$', '\g<1>.mp4', post['url'])
        elif re.match(r'^https?://imgur.com/[^/]+$', post['url']):
            typ = 'photo'
            post['url'] += '.png'
        elif re.match(r'^https?://imgur.com/r/[^/]+/[^/]+$', post['url']):
            typ = 'photo'
            post['url'] = re.sub(r'^https?://imgur.com/r/[^/]+/([^/]+)$',
                                 r'https://imgur.com/\g<1>.png',
                                 post['url'])
        elif post['domain'] == 'gfycat.com':
            typ = 'video'
            post['url'] = re.sub(r'https?://gfycat.com/(.+)',
                                 r'https://thumbs.gfycat.com/\g<1>-size_restricted.gif',
                                 post['url'])
        else:
            typ = 'link'
        self.logger.debug('Url:     ' + post['url'])
        self.logger.debug('Type:    ' + typ + '\n')
        return RedditPost(
            id=post['id'],
            title=post['title'],
            score=post['score'],
            subreddit=post['subreddit'],
            comments=comments,
            url=post['url'],
            datetime=post['created_utc'],
            type=typ
        )
