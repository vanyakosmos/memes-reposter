import logging


class BaseFetcher(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, *args, **kwargs):
        raise NotImplementedError('Must overwrite ::fetch method.')
