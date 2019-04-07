import typing

from applitools.common import (
    AppOutput,
    EyesError,
    RectangleSize,
    Region,
    SeleniumConfiguration,
    logger,
)
from applitools.common.visual_grid import (
    EmulationDevice,
    RenderBrowserInfo,
    RenderRequest,
    RunningRender,
    VGResource,
)
from applitools.core import NULL_REGION_PROVIDER, EyesBase
from applitools.core.capture import AppOutputWithScreenshot
from applitools.selenium.__version__ import __version__
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import Text, List, Dict, Any, Optional
    from requests import Response
    from applitools.common.metadata import AppEnvironment
    from applitools.common.visual_grid import RenderingInfo
    from applitools.common.match import MatchResult
    from applitools.common.test_results import TestResults
    from applitools.common.visual_grid import RenderStatusResults
    from applitools.selenium.fluent import SeleniumCheckSettings


class EyesConnector(EyesBase):
    def __init__(self, browser_info):
        # type: (RenderBrowserInfo) -> None
        super(EyesConnector, self).__init__()
        self.device = None
        self.device_size = None

        self._browser_info = browser_info  # type: RenderBrowserInfo
        self._current_uuid = None
        self._render_statuses = {}  # type: Dict[Text, RenderStatusResults]
        self._config = SeleniumConfiguration()

    def open(self, config):
        # type: (SeleniumConfiguration) -> None
        """Starts a new test without setting the viewport size of the AUT."""
        logger.info(
            "opening EyesConnector with viewport size: {}".format(
                self._browser_info.viewport_size
            )
        )
        self._config = config.clone()
        if self.device:
            self._config.viewport_size = self.device_size
        elif self._browser_info.viewport_size:
            self._config.viewport_size = self._browser_info.viewport_size
        else:
            # this means it's a emulationInfo
            if isinstance(self._browser_info.emulation_info, EmulationDevice):
                emu_device = self._browser_info.emulation_info
                self._config.viewport_size = RectangleSize.from_(emu_device)

        self._config.baseline_env_name = self._browser_info.baseline_env_name
        self._open_base()

    def get_resource(self, url):
        # type: (Text) -> Response
        return self._server_connector.download_resource(url)

    def render_put_resource(self, running_render, resource):
        # type: (RunningRender, VGResource) -> bool
        return self._server_connector.render_put_resource(running_render, resource)

    def render(self, *render_requests):
        # type: (*RenderRequest) -> List[RunningRender]
        return self._server_connector.render(*render_requests)

    # def render_status_by_ids(self, *ids):
    #     # type: (*Text) -> List[RenderStatusResults]
    #     return self._server_connector.render_status_by_ids(ids)

    def render_status_by_id(self, render_id):
        # type: (Text) -> RenderStatusResults
        return self._server_connector.render_status_by_id(render_id)

    def download_resource(self, url):
        # type: (Text) -> Response
        return self._server_connector.download_resource(url)

    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.selenium.visualgrid.python/{}".format(__version__)

    def _try_capture_dom(self):
        return None

    def get_viewport_size_static(self):
        return None

    def set_viewport_size_static(self, size):
        return None

    def _get_viewport_size(self):
        return None

    def _set_viewport_size(self, size):
        # type: (RectangleSize) -> Optional[Any]
        return None

    @property
    def _inferred_environment(self):
        # type: () -> str
        return "useragent: {}".format(self._browser_info.emulation_info)

    def _get_screenshot(self):
        return None

    @property
    def _title(self):
        # type: () -> Optional[Any]
        return None

    @property
    def _environment(self):
        # type: () -> AppEnvironment
        app_env = AppEnvironment(
            os=self.configuration.host_os,
            hosting_app=self.configuration.host_app,
            display_size=self.viewport_size,
            inferred=self._inferred_environment,
            device_info=self.device,
        )
        return app_env

    def render_info(self):
        # type: () -> RenderingInfo
        return self._server_connector.render_info()

    def check(self, name, check_settings, check_task_uuid):
        # type: (str, SeleniumCheckSettings, str) -> MatchResult
        self._current_uuid = check_task_uuid
        if name:
            check_settings = check_settings.with_name(name)
        check_result = self._check_window_base(
            NULL_REGION_PROVIDER, name, False, check_settings
        )
        self._current_uuid = None
        return check_result

    def close(self, throw_exception=True):
        # type: (bool) -> TestResults
        self._current_uuid = None
        return super(EyesConnector, self).close(throw_exception)

    def render_status_for_task(self, uuid, status):
        # type: (str, RenderStatusResults) -> None
        self._render_statuses[uuid] = status

    @property
    def render_status(self):
        # type: ()->RenderStatusResults
        status = self._render_statuses[self._current_uuid]
        if not status:
            raise EyesError("Got empty render status!")
        return status

    @property
    def screenshot_url(self):
        # type: () -> str
        return self.render_status.image_location

    @property
    def dom_url(self):
        # type: () -> str
        return self.render_status.dom_location

    def _get_app_output_with_screenshot(self, region, last_screenshot, check_settings):
        # type: (Region, EyesWebDriverScreenshot, SeleniumCheckSettings) -> AppOutputWithScreenshot
        title = self._title
        app_output = AppOutput(
            title=title,
            screenshot64=None,
            screenshot_url=self.screenshot_url,
            dom_url=self.dom_url,
        )
        result = AppOutputWithScreenshot(app_output, None)
        return result
