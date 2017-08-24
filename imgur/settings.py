from core import settings
from core.settings.fields import IntField


class ImgurSettings(settings.Settings):
    post_len = IntField(default=10)
    long_post_len = IntField(default=5)
    post_interval = IntField(default=60)
    db_clear_age = IntField(default=1 * 24 * 60 * 60)
    db_clear_interval = IntField(default=1 * 24 * 60 * 60)
