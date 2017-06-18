import logging

from .database import AbstractDB


class AbstractFilter(object):
    def __init__(self, db: AbstractDB):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def filter(self, data_chunks):
        """
        Args:
            data_chunks (list): list of objects that should be filtered.

        Returns:
            list
        """
