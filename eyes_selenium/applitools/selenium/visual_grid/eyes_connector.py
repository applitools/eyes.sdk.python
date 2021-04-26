import typing

from applitools.common import (
    AppEnvironment,
    AppOutput,
    EyesError,
    RectangleSize,
    Region,
    RenderInfo,
    VisualGridSelector,
    logger,
)
from applitools.common.ultrafastgrid import (
    IRenderBrowserInfo,
    JobInfo,
    RenderRequest,
    RunningRender,
    VGResource,
)
from applitools.core import (
    NULL_REGION_PROVIDER,
    EyesBase,
    RegionProvider,
    ServerConnector,
)
from applitools.core.capture import AppOutputWithScreenshot
from applitools.selenium import Configuration
from applitools.selenium.__version__ import __version__

if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Text, Union

    from requests import Response

    from applitools.common.match import MatchResult
    from applitools.common.test_results import TestResults
    from applitools.common.ultrafastgrid import (
        RenderBrowserInfo,
        RenderingInfo,
        RenderStatusResults,
    )
    from applitools.selenium.fluent import SeleniumCheckSettings


class EyesConnector(EyesBase):
    def __init__(
        self,
        browser_info,  # type: RenderBrowserInfo
        config,  # type: Configuration
        server_connector,  # type: ServerConnector
        agent_run_id,  # type: Text
        job_info=None,  # type: Optional[JobInfo]
    ):
        # type: (...) -> None
        super(EyesConnector, self).__init__()
        self.device_name = getattr(browser_info, "device_name", None)
        self._browser_info = browser_info  # type: IRenderBrowserInfo
        self._current_uuid = None
        self._render_statuses = {}  # type: Dict[Text, RenderStatusResults]
        self.set_configuration(config)
        self._server_connector = server_connector
        self._region_selectors = None
        self._regions = None
        self._job_info = job_info  # type: Optional[JobInfo]
        self._agent_run_id = agent_run_id

    def open(self, config):
        # type: (Configuration) -> None
        """Starts a new test without setting the viewport size of the AUT."""
        logger.info(
            "opening EyesConnector with viewport size: {}".format(
                self._browser_info.viewport_size
            )
        )
        # TODO: Add proper browser info handling
        self._config = config.clone()
        self._config.baseline_env_name = self._browser_info.baseline_env_name
        self._open_base()

    def render_put_resource(self, resource):
        # type: (VGResource) -> Text
        return self._server_connector.render_put_resource(resource)

    def render(self, *render_requests):
        # type: (*RenderRequest) -> List[RunningRender]
        return self._server_connector.render(*render_requests)

    def render_status_by_id(self, *render_ids):
        # type: (*Text) -> List[RenderStatusResults]
        return self._server_connector.render_status_by_id(*render_ids)

    def download_resource(self, url, cookies):
        # type: (Text, Dict) -> Response
        return self._server_connector.download_resource(url, cookies)

    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.selenium.visualgrid.python/{}".format(__version__)

    def _try_capture_dom(self):
        return None

    def get_viewport_size(self):
        return None

    def set_viewport_size(self, size):
        return None

    def _get_viewport_size(self):
        return None

    def _set_viewport_size(self, size):
        # type: (RectangleSize) -> Optional[Any]
        return None

    @property
    def _inferred_environment(self):
        # type: () -> str
        return ""

    def _get_screenshot(self):
        return None

    @property
    def _title(self):
        # type: () -> Text
        return ""

    @property
    def renderer(self):
        # type: () -> Text
        return self.job_info.renderer

    @property
    def job_info(self):
        # type: () ->  JobInfo
        if self._job_info:
            return self._job_info

        logger.warning("JobInfo is empty. Calling it again")
        render_requests = [
            RenderRequest(
                render_info=RenderInfo.from_(
                    size_mode=None,
                    region=None,
                    selector=None,
                    render_browser_info=self._browser_info,
                ),
                platform_name=self._browser_info.platform,
                browser_name=self._browser_info.browser,
            )
        ]

        self._job_info = self.server_connector.job_info(render_requests)[0]
        return self._job_info

    @property
    def _environment(self):
        # type: () -> Text
        return self.job_info.eyes_environment

    def render_info(self):
        # type: () -> RenderingInfo
        return self._server_connector.render_info()

    def check(
        self,
        check_settings,  # type: SeleniumCheckSettings
        check_task_uuid,  # type:  Text
        region_selectors,  # type: List[List[VisualGridSelector]]
        regions,  # type: List[Region]
        source,  # type: Optional[Text]
    ):
        # type:(...)->MatchResult
        self._current_uuid = check_task_uuid
        name = check_settings.values.name

        logger.debug("EyesConnector.check({}, {})".format(name, check_task_uuid))
        self._region_selectors = region_selectors
        self._regions = regions
        check_result = self._check_window_base(
            NULL_REGION_PROVIDER, False, check_settings, source
        )
        self._current_uuid = None
        self._region_selectors = []
        self._regions = []
        return check_result

    def close(self, raise_ex=True):
        # type: (bool) -> TestResults
        self._current_uuid = None
        return super(EyesConnector, self).close(raise_ex)

    def render_status_for_task(self, uuid, status):
        # type: (str, RenderStatusResults) -> None
        logger.debug(
            "render_status_for_task: uuid: {} \n\tstatus: {}".format(uuid, status)
        )
        self._current_uuid = uuid
        self._render_statuses[uuid] = status

    @property
    def render_status(self):
        # type: ()->RenderStatusResults
        status = self._render_statuses.get(self._current_uuid)
        logger.debug("task.uuid: {}, status: {}".format(self._current_uuid, status))
        if not status:
            raise EyesError(
                "Got empty render status with key {}!".format(self._current_uuid)
            )
        return status

    def _match_window(self, region_provider, check_settings, source):
        # type: (RegionProvider, SeleniumCheckSettings, Optional[Text]) -> MatchResult
        # Update retry timeout if it wasn't specified.
        retry_timeout_ms = -1  # type: int
        if check_settings:
            retry_timeout_ms = check_settings.values.timeout

        region = region_provider.get_region()
        logger.debug(
            "params: ([{}], {}, {} ms)".format(
                region, check_settings.values.name, retry_timeout_ms
            )
        )

        app_output = self._get_app_output_with_screenshot(None, None, check_settings)
        image_match_settings = self._match_window_task.create_image_match_settings(
            check_settings, self
        )
        return self._match_window_task.perform_match(
            app_output=app_output,
            replace_last=False,
            image_match_settings=image_match_settings,
            eyes=self,
            user_inputs=self._user_inputs,
            check_settings=check_settings,
            render_id=self.render_status.render_id,
            region_selectors=self._region_selectors,
            regions=self._regions,
            source=source,
        )

    def _get_app_output_with_screenshot(self, region, last_screenshot, check_settings):
        # type: (None, None, SeleniumCheckSettings)->AppOutputWithScreenshot
        logger.debug("render_task.uuid: {}".format(self._current_uuid))
        app_output = AppOutput(
            title=self._title,
            screenshot_bytes=None,
            screenshot_url=self.render_status.image_location,
            dom_url=self.render_status.dom_location,
            viewport=self.render_status.visual_viewport,
        )
        result = AppOutputWithScreenshot(app_output, None)
        return result
