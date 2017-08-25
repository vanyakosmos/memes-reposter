from core.channel import BaseChannel
from core.decorators import log
from settings import REDIS_URL, IMGUR_CHANNEL_ID, CLEAR_AGE
from .pipes import ImgurPipe
from .store import ImgurStore
from .settings import ImgurSettings
from .commands import TagsCommander, SettingsCommander


class ImgurChannel(BaseChannel):
    def __init__(self):
        super().__init__()
        self.store = ImgurStore('imgur',
                                url=REDIS_URL,
                                clear_age=CLEAR_AGE)
        self.settings = ImgurSettings(self.store)

        self.commanders = [
            TagsCommander(self.store),
            SettingsCommander(self.settings, restart_callback=self.start),
        ]

    @property
    def commands_handlers(self):
        return [commander.handler for commander in self.commanders]

    def get_channel_id(self):
        return IMGUR_CHANNEL_ID

    def get_pipes(self):
        return [ImgurPipe()]

    @log
    def start(self):
        for pipe in self.pipes:
            pipe.set_up(self.channel_id, self.updater, self.store, self.settings)
            pipe.start_posting_cycle()

    def help_text(self):
        usages = [
            commander.get_usage()
            for commander in self.commanders
        ]
        return '\n'.join(usages)
