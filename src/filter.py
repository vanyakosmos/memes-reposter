from typing import List

from telegram import MAX_FILESIZE_DOWNLOAD

from autoposter import AbstractFilter
from settings import BANNED_TAGS, IMAGES_FOR_LONG_POST, IMAGES_PER_POST

from settings import MAX_VIDEO_SIZE, MAX_IMAGE_SIZE, MIN_DIM_RATIO
from .fetcher import AlbumFetcher
from .wrappers import Post, Image


class ImageValidatorMixin(object):
    @staticmethod
    def valid_image(image: Image):
        normal_image_size = image.animated or image.size < MAX_IMAGE_SIZE
        normal_size = image.size < MAX_VIDEO_SIZE
        large_size = not normal_size and image.size < MAX_FILESIZE_DOWNLOAD
        good_ration = image.width / image.height > MIN_DIM_RATIO and image.height / image.width > MIN_DIM_RATIO

        return normal_image_size and (normal_size or large_size) and good_ration


class PostsFilter(AbstractFilter, ImageValidatorMixin):
    def filter(self, posts):
        """
        Args:
            posts (List[dict]): Posts obtained from Imgur gallery.

        Returns:
            List[Post]: list of Post objects.
        """
        filtered_posts = []
        for post_dict in posts:
            post = Post(post_dict)

            if post.id in self.db:
                continue

            for bad_tag in BANNED_TAGS:
                if bad_tag in post.tags:
                    continue

            post.is_dump = post.images_count > IMAGES_PER_POST
            album_fetcher = AlbumFetcher(post_id=post.id)
            images = self.filtrate_images(images_list=post_dict.get('images', []),
                                          post=post, album_fetcher=album_fetcher)
            if images:
                post.images = images
                filtered_posts.append(post)

        return filtered_posts

    def filtrate_images(self, images_list: list, post: Post, album_fetcher: AlbumFetcher):
        images = []
        if post.is_album:
            response = album_fetcher.fetch()
            if response.success:
                album = response.data
                limit = IMAGES_FOR_LONG_POST if post.is_dump else IMAGES_PER_POST
                images = self.collect_images(album, limit)
        else:
            image = Image(post.post_dict)
            if self.valid_image(image):
                images.append(image)
        return images

    def collect_images(self, images: List[dict], limit: int) -> List[Image]:
        picked_images = []
        for image_dict in images:
            if len(picked_images) >= limit:
                break
            image = Image(image_dict)
            if self.valid_image(image):
                picked_images.append(image)
        return picked_images


class SubredditFilter(AbstractFilter, ImageValidatorMixin):
    def filter(self, posts):
        """
        Args:
            posts (List[dict]): Posts obtained from Imgur gallery.

        Returns:
            List[Post]: list of Post objects.
        """
        filtered_posts = []
        for post_dict in posts:
            post = Post(post_dict)

            if post.id in self.db:
                continue

            if post.score < 600:
                continue

            if post.is_album:
                pass  # todo
            else:
                image = Image(post.post_dict)
                if self.valid_image(image):
                    post.images = [image]
                    filtered_posts.append(post)

        return filtered_posts
