from applitools.eyes_core import EyesBase

from . import __version__


class Eyes(EyesBase):
    @property
    def base_agent_id(self):
        return "eyes_images.python/{version}".format(version=__version__)

