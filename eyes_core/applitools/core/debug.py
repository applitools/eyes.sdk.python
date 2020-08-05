from abc import abstractmethod
from datetime import datetime

import attr

from applitools.common.utils import image_utils
from applitools.common.utils.general_utils import get_env_with_prefix


@attr.s(slots=True)
class DebugScreenshotsProvider(object):
    """Interface for saving debug screenshots."""

    _prefix = attr.ib(
        factory=lambda: get_env_with_prefix("DEBUG_SCREENSHOT_PREFIX", "screenshot_")
    )
    _path = attr.ib(factory=lambda: get_env_with_prefix("DEBUG_SCREENSHOT_PATH", ""))

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


class NullDebugScreenshotsProvider(DebugScreenshotsProvider):
    """A mock debug screenshot provider."""

    def save(self, image, suffix):
        pass


class FileDebugScreenshotsProvider(DebugScreenshotsProvider):
    """ A debug screenshot provider for saving screenshots to file."""

    def save(self, image, suffix):
        now = datetime.now().strftime("%H:%M:%S")
        suffix = "{}-{}".format(self._image_counter, suffix)
        self._image_counter += 1

        filename = "{path}/{prefix}_{timestamp}_{suffix}.png".format(
            path=self.path, prefix=self.prefix, timestamp=now, suffix=suffix
        )
        image_utils.save_image(image, filename)
