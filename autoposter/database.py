import logging


class AbstractDB(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def add(self, item_id, datetime):
        """
        Store items id and datetime so it can be deleted by ``clear()`` method.

        Args:
            item_id:
            datetime:
        """
        pass

    def clear(self, period: int):
        """
        Remove from database old data.
        Args:
            period:
        """
        pass

    def keys(self):
        """
        Returns: set of items ids.
        """
        pass
