from __future__ import absolute_import, unicode_literals

from robot.api import logger
from robot.utils import ConnectionCache, is_string

from applitools.selenium import Eyes


def is_noney(item):
    return item is None or is_string(item) and item.upper() == "NONE"


class EyesCache(ConnectionCache):
    def __init__(self):
        ConnectionCache.__init__(self, no_current_msg="No current eyes")
        self._closed = set()

    @property
    def eyes(self):
        # type: () -> Eyes
        return self._connections

    @property
    def active_eyes(self):
        open_eyes = []
        for eyes in self._connections:
            if eyes not in self._closed:
                open_eyes.append(eyes)
        return open_eyes

    @property
    def active_eyes_ids(self):
        open_eyes_ids = []
        for index, driver in enumerate(self._connections):
            if driver not in self._closed:
                open_eyes_ids.append(index + 1)
        return open_eyes_ids

    @property
    def active_aliases(self):
        return self._aliases

    def close(self):
        if not self.current:
            return
        eyes = self.current
        error = self._quit(eyes, None)
        for alias in self._aliases:
            if self._aliases[alias] == self.current_index:
                del self._aliases[alias]
        self.current = self._no_current
        self._closed.add(eyes)
        if error:
            raise error

    def close_all(self):
        error = None
        for eyes in self._connections:
            if eyes not in self._closed:
                error = self._quit(eyes, error)
        self.empty_cache()
        if error:
            raise error
        return self.current

    def _quit(self, driver, error):
        try:
            driver.quit()
        except Exception as exception:
            logger.error("When closing browser, received exception: %s" % exception)
            error = exception
        return error

    def get_index(self, alias_or_index):
        index = self._get_index(alias_or_index)
        try:
            driver = self.get_connection(index)
        except RuntimeError:
            return None
        return None if driver in self._closed else index

    def _get_index(self, alias_or_index):
        alias_or_index = None if is_noney(alias_or_index) else alias_or_index
        try:
            return self.resolve_alias_or_index(alias_or_index)
        except AttributeError:
            pass
        except ValueError:
            return None
        # TODO: This try/except block can be removed when minimum
        #  required Robot Framework version is 3.3 or greater.
        try:
            return self._resolve_alias_or_index(alias_or_index)
        except ValueError:
            return None
