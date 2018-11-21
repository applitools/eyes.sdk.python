import typing as tp

from PIL import Image

from applitools.eyes_core import EyesBase, logger, EyesError
from .__version__ import __version__
from .target import Target
from .capture import EyesImagesScreenshot


class Eyes(EyesBase):
    def __init__(self, server_url=EyesBase.DEFAULT_EYES_SERVER):
        super(Eyes, self).__init__(server_url)
        self._title = None
        self._screenshot = None
        self._inferred = None

    @property
    def _full_agent_id(self):
        if self.agent_id is None:
            return self.base_agent_id
        return "%s [%s]" % (self.agent_id, self.base_agent_id)

    @property
    def base_agent_id(self):
        # return "eyes.selenium.python/{version}".format(version=__version__)
        return "eyes.images.python/{version}".format(version=__version__)

    @property
    def title(self):
        return self._title

    def _get_inferred_environment(self):
        return self._inferred

    def get_viewport_size(self):
        return self._viewport_size

    def set_viewport_size(self, viewport_size):
        self._viewport_size = viewport_size

    def _assign_viewport_size(self):
        pass

    def get_screenshot(self, **kwargs):
        return self._screenshot

    def try_capture_dom(self):
        return None

    def open(self, app_name, test_name, dimension=None):
        self.open_base(app_name, test_name, dimension)

    def check(self, name, target):
        # type: (tp.Text, Target) -> bool
        if self.is_disabled:
            return False
        return self._check_image(name, False, target)

    def check_image(self, image, tag=None, ignore_mismatch=False, retry_timeout=-1):
        if self.is_disabled:
            return
        logger.info(
            'check_image(Image {}, tag {}, ignore_mismatch {}, retry_timeout {}'.format(image, tag, ignore_mismatch,
                                                                                        retry_timeout))
        return self._check_image(tag, ignore_mismatch, Target().image(image).timeout(retry_timeout))

    def check_region(self, image, region, tag=None, ignore_mismatch=False, retry_timeout=-1):
        if self.is_disabled:
            return
        logger.info(
            'check_region(Image {}, region {}, tag {}, '
            'ignore_mismatch {}, retry_timeout {}'.format(image, region, tag,
                                                          ignore_mismatch,
                                                          retry_timeout))
        return self._check_image(tag, ignore_mismatch, Target().region(image, region).timeout(retry_timeout))

    def _check_image(self, name, ignore_mismatch, target):
        # type: (tp.Text, bool, Target) -> bool
        # Set the title to be linked to the screenshot.
        self._title = name if name else ''

        if not self.is_open():
            self.abort_if_not_closed()
            raise EyesError('you must call open() before checking')

        image = target._image  # type: Image.Image
        self._screenshot = EyesImagesScreenshot(image)
        if not self._viewport_size:
            self.set_viewport_size(dict(width=image.width, height=image.height))

        match_result = self._check_window_base(name, ignore_mismatch, target)
        self._screenshot = None
        self._title = None
        return match_result['as_expected']

    def _get_environment(self):
        app_env = {'os':          self.host_os, 'hostingApp': self.host_app,
                   'displaySize': self._viewport_size,
                   'inferred':    self._get_inferred_environment()}
        return app_env
