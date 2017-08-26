from core.channel import BaseChannel
from core.decorators import log
from settings import REDIS_URL, IMGUR_CHANNEL_ID, CLEAR_AGE
from .pipes import ImgurPipe
from .store import ImgurStore
from .settings import ImgurSettings
from core.commands import SettingsCommander, ActivityCommander
from .commands import TagsCommander


class ImgurChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.store = ImgurStore('imgur',
                                url=REDIS_URL,
                                clear_age=CLEAR_AGE)
        self.settings = ImgurSettings(self.store)

        self.commanders = [
            TagsCommander('tags', self.store),
            SettingsCommander('sets', self.settings),
            ActivityCommander('act', self.store),
        ]

    def get_channel_id(self):
        return IMGUR_CHANNEL_ID

    def get_pipes(self):
        return [ImgurPipe()]

    @property
    def commands_handlers(self):
        return [commander.handler for commander in self.commanders]

    @log
    def start(self):
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater, self.store, self.settings)
            pipe.start_posting_cycle()

    def help_text(self):
        return '\n'.join([c.get_usage() for c in self.commanders])
