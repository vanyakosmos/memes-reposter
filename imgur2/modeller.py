from core2.modeller import BaseModeller
from .models import Post
from .settings import ImgurSettings


class ImgurModeller(BaseModeller):
    def __init__(self, settings: ImgurSettings):
        super().__init__()
        self.settings = settings

    def model(self, posts, *args, **kwargs):
        images_per_post = self.settings.post_len
        images_per_long_post = self.settings.long_post_len
        return [Post(json, images_per_post, images_per_long_post) for json in posts]
