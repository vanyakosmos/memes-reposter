from core2 import settings
from core2.settings.fields import IntField, FloatFiled


class ImgurSettings(settings.Settings):
    post_len = IntField(default=10)
    long_post_len = IntField(default=5)
    post_interval = IntField(default=20 * 60)
    score = IntField(default=1000)
    max_dim = FloatFiled(default=1.5)
