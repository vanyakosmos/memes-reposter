from core import settings
from core.settings.fields import IntField


class ImgurSettings(settings.Settings):
    post_len = IntField(default=10)
    long_post_len = IntField(default=5)
    post_interval = IntField(default=20 * 60)
