from core.channel import BaseChannel
from core.decorators import log
from settings import REDIS_URL, REDDIT_CHANNEL_ID, CLEAR_AGE
from .pipes import RedditPipe
from .store import RedditStore
from .settings import RedditSettings
from core.commands import SettingsCommander
from .commands import SubredditsCommander


class RedditChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.store = RedditStore('reddit',
                                 url=REDIS_URL,
                                 clear_age=CLEAR_AGE)
        self.settings = RedditSettings(self.store)

        self.commanders = [
            SubredditsCommander('subs', self.store),
            SettingsCommander('sets', self.settings, restart_callback=self.start),
        ]

    def get_channel_id(self):
        return REDDIT_CHANNEL_ID

    def get_pipes(self):
        return [RedditPipe()]

    @property
    def commands_handlers(self):
        return [c.handler for c in self.commanders]

    @log
    def start(self):
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater, self.store)
            pipe.start_posting_cycle()

    def help_text(self):
        return '\n'.join([c.get_usage() for c in self.commanders])
