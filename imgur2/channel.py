from core2.channel import BaseChannel
from core2.commands import ActivityCommander, SettingsCommander
from core2.decorators import log
from settings import CLEAR_AGE, IMGUR_CHANNEL_ID, MONGODB_URI
from .commands import TagsCommander
from .pipes import ImgurPipe
from .settings import ImgurSettings
from .store import ImgurStore


class ImgurChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.store = ImgurStore('imgur',
                                url=MONGODB_URI,
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
            pipe.set_up(self.channel_id, self.updater, store=self.store, settings=self.settings)
            pipe.start_posting_cycle()

    def help_text(self):
        return '\n'.join([c.get_usage() for c in self.commanders])
