import logging


class AbstractDB(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def add(self, item_id, datetime):
        pass

    def clear(self, period: int):
        pass

    def keys(self):
        pass
