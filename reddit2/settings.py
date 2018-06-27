from core2.settings import Settings
from core2.settings.fields import IntField


class RedditSettings(Settings):
    post_interval = IntField(default=20 * 60)
