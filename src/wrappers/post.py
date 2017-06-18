from typing import List

from .image import Image


class Post(object):
    """
    Wrapping a post dictionary obtained from Imgur.
    """
    def __init__(self, post_dict: dict):
        """
        Args:
            post_dict (dict): Dictionary of post parameters.
        """
        self.post_dict = post_dict
        self._tags = ['#' + tag["name"] for tag in self.post_dict['tags']]
        self._images: List[Image] or None = None
        self._is_dump = False

    def __str__(self):
        return f"Post(id='{self.id}', link='{self.link}', title='{self.title[:20]}', desc='{self.desc[:20]}')"

    @property
    def id(self) -> str:
        return self.post_dict.get('id')

    @property
    def title(self) -> str:
        title = self.post_dict.get('title')
        if title:
            return title.strip()
        return ''

    @property
    def desc(self) -> str:
        desc = self.post_dict.get('description')
        if desc:
            return desc.strip()
        return ''

    @property
    def score(self):
        return self.post_dict['score']

    @property
    def datetime(self) -> int:
        return self.post_dict.get('datetime')

    @property
    def link(self) -> str:
        if self.is_album:
            return self.post_dict.get('link')
        else:
            return "http://imgur.com/" + self.id

    @property
    def tags(self) -> List[str]:
        return self._tags

    @tags.setter
    def tags(self, tags: list):
        self._tags.extend(tags)

    @property
    def images_count(self) -> int:
        return self.post_dict.get('images_count', 1)

    @property
    def is_album(self) -> bool:
        return self.post_dict.get('is_album')

    @property
    def is_dump(self) -> bool:
        return self._is_dump

    @is_dump.setter
    def is_dump(self, is_dump):
        self._is_dump = is_dump

    @property
    def images(self) -> list:
        if self._images:
            return self._images
        else:
            return []

    @images.setter
    def images(self, images):
        self._images = images
