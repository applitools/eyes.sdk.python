import typing as tp

from PIL import Image

from applitools.core import EyesBase, logger, EyesError, Region
from .__version__ import __version__
from .target import Target
from .capture import EyesImagesScreenshot

if tp.TYPE_CHECKING:
    from applitools.core.utils.custom_types import ViewPort, AppEnvironment


class Eyes(EyesBase):
    def __init__(self, server_url=EyesBase.DEFAULT_EYES_SERVER):
        # type: (tp.Text) -> None
        super(Eyes, self).__init__(server_url)
        self._raw_title = None  # type: tp.Optional[tp.Text]
        self._screenshot = None  # type: tp.Optional[EyesImagesScreenshot]
        self._inferred = None  # type: tp.Optional[tp.Text]

    @property
    def full_agent_id(self):
        # type: () -> tp.Text
        if self.agent_id is None:
            return self.base_agent_id
        return "%s [%s]" % (self.agent_id, self.base_agent_id)

    @property
    def base_agent_id(self):
        # type: () -> tp.Text
        return "eyes.images.python/{version}".format(version=__version__)

    @property
    def _title(self):
        return self._raw_title

    @property
    def _inferred_environment(self):
        # type: () -> tp.Text
        if self._inferred:
            return self._inferred
        return ""

    def get_viewport_size(self):
        # type: () -> ViewPort
        return self._viewport_size

    def set_viewport_size(self, size):
        # type: (ViewPort) -> None
        self._viewport_size = size

    def _ensure_viewport_size(self):
        pass

    def get_screenshot(self, **kwargs):
        # type: (**tp.Dict) -> EyesImagesScreenshot
        return self._screenshot

    def _try_capture_dom(self):
        # type: () -> None
        return None

    def open(self, app_name, test_name, dimension=None):
        # type: (tp.Text, tp.Text, tp.Optional[ViewPort]) -> None
        self._open_base(app_name, test_name, dimension)

    def check(self, name, target):
        # type: (tp.Text, Target) -> bool
        if self.is_disabled:
            return False
        return self._check_image(name, False, target)

    def check_image(self, image, tag=None, ignore_mismatch=False, retry_timeout=-1):
        # type: (tp.Union[Image.Image, tp.Text], tp.Optional[tp.Text], bool, int) -> tp.Optional[bool]
        if self.is_disabled:
            return None
        logger.info(
            'check_image(Image {}, tag {}, ignore_mismatch {}, retry_timeout {}'.format(image, tag, ignore_mismatch,
                                                                                        retry_timeout))
        return self._check_image(tag, ignore_mismatch, Target().image(image).timeout(retry_timeout))

    def check_region(self, image, region, tag=None, ignore_mismatch=False, retry_timeout=-1):
        # type: (Image.Image, Region, tp.Optional[tp.Text], bool, int) -> tp.Optional[bool]
        if self.is_disabled:
            return None
        logger.info(
            'check_region(Image {}, region {}, tag {}, '
            'ignore_mismatch {}, retry_timeout {}'.format(image, region, tag,
                                                          ignore_mismatch,
                                                          retry_timeout))
        return self._check_image(tag, ignore_mismatch, Target().region(image, region).timeout(retry_timeout))

    def _check_image(self, name, ignore_mismatch, target):
        # type: (tp.Text, bool, Target) -> bool
        # Set the title to be linked to the screenshot.
        self._raw_title = name if name else ''

        if not self.is_open:
            self.abort_if_not_closed()
            raise EyesError('you must call open() before checking')

        image = target._image  # type: Image.Image
        self._screenshot = EyesImagesScreenshot(image)
        if not self._viewport_size:
            self.set_viewport_size(dict(width=image.width, height=image.height))

        match_result = self._check_window_base(name, -1, target, ignore_mismatch)
        self._screenshot = None
        self._raw_title = None
        return match_result['as_expected']

    @property
    def _environment(self):
        # type: () -> AppEnvironment
        app_env = {'os':          self.host_os, 'hostingApp': self.host_app,
                   'displaySize': self._viewport_size,
                   'inferred':    self._inferred_environment}
        return app_env
