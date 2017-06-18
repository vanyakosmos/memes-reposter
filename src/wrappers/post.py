from typing import List

from settings import IMAGES_PER_POST, IMAGES_FOR_LONG_POST
from src.fetcher import AlbumFetcher
from .image import Image


class Post(object):
    """
    Wrapping a post dictionary obtained from Imgur.
    """
    def __init__(self, post: dict, album_fetcher: AlbumFetcher):
        """
        Args:
            post (dict): Dictionary of post parameters.
        """
        self.post = post
        self.album_fetcher = album_fetcher
        self.cache = {}

    def __str__(self):
        return f"Post(id='{self.id}', link='{self.link}', title='{self.title[:20]}', desc='{self.desc[:20]}')"

    @property
    def id(self) -> str:
        return self.post.get('id')

    @property
    def title(self) -> str:
        title = self.post.get('title')
        if title:
            return title.strip()
        return ''

    @property
    def desc(self) -> str:
        desc = self.post.get('description')
        if desc:
            return desc.strip()
        return ''

    @property
    def datetime(self) -> int:
        return self.post.get('datetime')

    @property
    def link(self) -> str:
        if self.is_album:
            return self.post.get('link')
        else:
            return "http://imgur.com/" + self.id

    @property
    def tags(self) -> List[str]:
        if 'tags' in self.cache:
            return self.cache['tags']
        else:
            tags = ['#' + tag["name"] for tag in self.post['tags']]
            self.cache['tags'] = tags
            return tags

    @property
    def images_count(self) -> int:
        return self.post.get('images_count', 1)

    @property
    def is_album(self) -> bool:
        return self.post.get('is_album')

    @property
    def is_dump(self) -> bool:
        return self.images_count > IMAGES_PER_POST

    @property
    def images(self) -> list:
        if 'images' in self.cache:
            return self.cache['images']
        else:
            images = []
            if self.is_album:
                if self.images_count <= 3:
                    images = self.collect_images(self.post['images'], 3)
                else:
                    response = self.album_fetcher.fetch(self.id)
                    if response.success:
                        album = response.data
                        limit = IMAGES_FOR_LONG_POST if self.is_dump else IMAGES_PER_POST
                        images = self.collect_images(album, limit)
            else:
                image = Image(self.post)
                if image.valid:
                    images.append(image)
            self.cache['images'] = images
            return images

    @property
    def valid(self) -> bool:
        if 'valid' in self.cache:
            return self.cache['valid']
        else:
            return len(self.images) > 0

    @staticmethod
    def collect_images(images: List[dict], limit: int) -> List[Image]:
        picked_images = []
        for image_dict in images:
            if len(picked_images) >= limit:
                break
            image = Image(image_dict)
            if image.valid:
                picked_images.append(image)
        return picked_images
