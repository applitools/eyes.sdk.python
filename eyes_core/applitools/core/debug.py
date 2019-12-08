import os
from abc import abstractmethod
from datetime import datetime

import attr

from applitools.common.utils import image_utils
from applitools.common.utils.general_utils import get_env_with_prefix


@attr.s
class DebugScreenshotProvider(object):
    """Interface for saving debug screenshots."""

    DEFAULT_PREFIX = get_env_with_prefix("DEBUG_SCREENSHOT_PREFIX", "screenshot_")
    DEFAULT_PATH = get_env_with_prefix("DEBUG_SCREENSHOT_PATH", "")

    _prefix = attr.ib(default=DEFAULT_PREFIX)
    _path = attr.ib(default=DEFAULT_PATH)

    def __attrs_post_init__(self):
        self._image_counter = 0

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        if value:
            self._prefix = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value:
            self._path = value.rstrip("/")

    @abstractmethod
    def save(self, image, suffix):
        pass


class NullDebugScreenshotProvider(DebugScreenshotProvider):
    """A mock debug screenshot provider."""

    def save(self, image, suffix):
        pass


class FileDebugScreenshotProvider(DebugScreenshotProvider):
    """ A debug screenshot provider for saving screenshots to file."""

    def save(self, image, suffix):
        now = datetime.now().strftime("%H:%M:%S")
        suffix = "{}-{}".format(self._image_counter, suffix)
        self._image_counter += 1

        filename = "{path}/{prefix}_{timestamp}_{suffix}.png".format(
            path=self.path, prefix=self.DEFAULT_PREFIX, timestamp=now, suffix=suffix
        )
        image_utils.save_image(image, filename)
