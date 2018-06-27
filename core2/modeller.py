import logging


class BaseModeller(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def model(self, data, *args, **kwargs):
        self.logger.debug('Modelling...')
        posts = data
        return posts
