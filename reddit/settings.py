from core.settings import Settings
from core.settings.fields import IntField


class RedditSettings(Settings):
    post_interval = IntField(default=20 * 60)
