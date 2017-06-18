import logging


class Response(object):
    def __init__(self, success, data):
        self._success = success
        self._data = data

    @property
    def success(self):
        return self._success

    @property
    def data(self):
        if self.success:
            return self._data
        else:
            return []


class AbstractFetcher(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self) -> Response:
        """
        Obtain data and setup ``self._success`` and ``self._data`` parameters.
        """
        pass

    def log_status(self, code: int):
        if code == 200:
            self.logger.info(f"Successfully received data.")
        else:
            self.logger.warning(f"Failed to receive data.")
