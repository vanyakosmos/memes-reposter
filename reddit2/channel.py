from core2.channel import BaseChannel
from core2.commands import ActivityCommander, SettingsCommander
from core2.decorators import log
from settings import CLEAR_AGE, REDDIT_CHANNEL_ID, MONGODB_URI
from .commands import SubredditsCommander
from .pipes import RedditPipe
from .settings import RedditSettings
from .store import RedditStore


class RedditChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.store = RedditStore(name='reddit',
                                 url=MONGODB_URI,
                                 clear_age=CLEAR_AGE)
        self.settings = RedditSettings(self.store)

        self.commanders = [
            SubredditsCommander('subs', self.store),
            SettingsCommander('sets', self.settings),
            ActivityCommander('act', self.store),
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
            pipe.set_up(self.channel_id, self.updater, store=self.store, settings=self.settings)
            pipe.start_posting_cycle()

    def help_text(self):
        return '\n'.join([c.get_usage() for c in self.commanders])
