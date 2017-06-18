import logging


class AbstractDB(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __len__(self):
        pass

    def __contains__(self, item: str or dict):
        pass

    def add(self, item: dict):
        pass

    def clear(self, period: int):
        pass
