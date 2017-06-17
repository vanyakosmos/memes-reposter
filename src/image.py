from telegram import MAX_FILESIZE_DOWNLOAD

from settings import MAX_VIDEO_SIZE, MAX_IMAGE_SIZE, MIN_DIM_RATIO


class Image(object):
    """
    wrapping a image dictionary obtained from Imgur.
    """
    def __init__(self, image: dict):
        """
        Args (dict):
            image: Dictionary of image parameters.
        """
        self.image = image

    def __str__(self):
        return f"Image(id='{self.id}', src='{self.src}', size='{self.size}', " \
               f"width='{self.width}', height='{self.height}', desc='{len(self.desc) > 0}')"

    @property
    def id(self):
        return self.image['id']

    @property
    def title(self) -> str:
        title = self.image.get('title')
        if title:
            return title.strip()
        return ''

    @property
    def desc(self) -> str:
        desc = self.image.get('description')
        if desc:
            return desc.strip()
        return ''

    @property
    def src(self) -> str:
        # https://example.com/*.(mp4 | jpg | png)
        return self.image['mp4'] if self.animated else self.image['link']

    @property
    def size(self) -> int:
        return self.image.get('size')

    @property
    def width(self) -> int:
        return self.image.get('width')

    @property
    def height(self) -> int:
        return self.image.get('height')

    @property
    def animated(self) -> bool:
        return self.image.get('animated', False)

    @property
    def type(self) -> str:
        # image/png, image/jpeg, image/gif
        return self.image.get('type')

    @property
    def valid(self) -> bool:
        normal_image_size = self.animated or self.size < MAX_IMAGE_SIZE
        normal_size = self.size < MAX_VIDEO_SIZE
        large_size = not normal_size and self.size < MAX_FILESIZE_DOWNLOAD
        good_ration = self.width / self.height > MIN_DIM_RATIO and self.height / self.width > MIN_DIM_RATIO

        return normal_image_size and (normal_size or large_size) and good_ration
