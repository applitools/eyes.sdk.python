from __future__ import unicode_literals

import json
import typing
from abc import abstractmethod
from enum import Enum
from time import time

import attr
from selenium.webdriver.common.by import By

from applitools.common.utils import ABC, datetime_utils
from applitools.common.utils.json_utils import JsonInclude, to_json
from applitools.selenium import resource
from applitools.selenium.fluent import FrameLocator

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Text, Union

    from structlog import BoundLogger

    from applitools.selenium import EyesWebDriver


MAX_CHUNK_BYTES_IOS = 10 * 1024 * 1024
MAX_CHUNK_BYTES_GENERIC = 50 * 1024 * 1024


class DomSnapshotFailure(Exception):
    pass


class DomSnapshotScriptError(DomSnapshotFailure):
    pass


class DomSnapshotTimeout(DomSnapshotFailure):
    pass


def create_dom_snapshot(
    driver,  # type: EyesWebDriver
    logger,  # type: BoundLogger
    dont_fetch_resources,  # type: bool
    skip_resources,  # type: Optional[List[Text]]
    timeout_ms,  # type: int
    cross_origin_rendering,  # type: bool
    use_cookies,  # type: bool
):
    # type: (...) -> Dict
    is_ie = driver.user_agent.is_internet_explorer
    script_type = DomSnapshotScriptForIE if is_ie else DomSnapshotScriptGeneric
    script = script_type(driver)
    is_ios = "ios" in driver.desired_capabilities.get("platformName", "").lower()
    chunk_byte_length = MAX_CHUNK_BYTES_IOS if is_ios else MAX_CHUNK_BYTES_GENERIC
    snapshotter = RecursiveSnapshotter(
        driver,
        script,
        logger,
        timeout_ms,
        chunk_byte_length,
        cross_origin_rendering,
        use_cookies,
        dont_fetch_resources=dont_fetch_resources,
        skip_resources=skip_resources,
        serialize_resources=True,
    )
    try:
        return snapshotter.create_cross_frames_dom_snapshots()
    except Exception:
        logger.info(
            "Failed to create dom-snapshot, retrying ignoring failing frames",
            exc_info=True,
        )
        snapshotter.should_skip_failed_frames = True
        return snapshotter.create_cross_frames_dom_snapshots()


@attr.s
class ProcessPageArgs(object):
    show_logs = attr.ib(
        type=bool, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]
    use_session_cache = attr.ib(
        type=bool, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]
    dont_fetch_resources = attr.ib(
        type=bool, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]
    fetch_timeout = attr.ib(
        type=int, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[int]
    skip_resources = attr.ib(
        type=list, metadata={JsonInclude.NON_NONE: True}
    )  # type: List[Text]
    compress_resources = attr.ib(
        type=bool, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]
    serialize_resources = attr.ib(
        type=bool, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]


@attr.s
class PollResultArgs(object):
    chunk_byte_length = attr.ib(
        type=int, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[int]


class ProcessPageStatus(Enum):
    SUCCESS = "SUCCESS"
    WIP = "WIP"
    ERROR = "ERROR"
    SUCCESS_CHUNKED = "SUCCESS_CHUNKED"


@attr.s
class ProcessPageResult(object):
    status = attr.ib(type=ProcessPageStatus)  # type: ProcessPageStatus
    done = attr.ib(type=bool, default=None)  # type: Optional[bool]
    error = attr.ib(type=str, default=None)  # type: Optional[Text]
    value = attr.ib(default=None)  # type: Optional[Union[Dict,Text]]

    @classmethod
    def from_json(cls, status_json):
        # attr_from_json doesn't support untyped dict fields for now
        status_json = json.loads(status_json)
        return cls(
            status=ProcessPageStatus(status_json["status"]),
            done=status_json.get("done"),
            error=status_json.get("error"),
            value=status_json.get("value"),
        )


class DomSnapshotScript(ABC):
    """Base class for different flavors of dom-snapshot script"""

    @abstractmethod
    def process_page_script_code(self, args):
        # type: (Text) -> Text
        pass

    @abstractmethod
    def poll_result_script_code(self, args):
        # type: (Text) -> Text
        pass

    def __init__(self, driver):
        # type: (EyesWebDriver) -> None
        self._driver = driver

    def run(
        self,
        show_logs=None,  # type: Optional[bool]
        use_session_cache=None,  # type: Optional[bool]
        dont_fetch_resources=None,  # type: Optional[bool]
        fetch_timeout=None,  # type: Optional[int]
        skip_resources=None,  # type: Optional[List[Text]]
        compress_resources=None,  # type: Optional[bool]
        serialize_resources=None,  # type: Optional[bool]
    ):
        # type: (...) -> ProcessPageResult
        return self._run_script(
            locals(), ProcessPageArgs, self.process_page_script_code
        )

    def poll_result(self, chunk_byte_length=None):
        # type: (Optional[int]) -> ProcessPageResult
        return self._run_script(locals(), PollResultArgs, self.poll_result_script_code)

    def _run_script(self, args, args_type, code_gen_func):
        # type: (Dict[Text, Any], type, Callable[[Text], Text]) -> ProcessPageResult
        args = {k: v for k, v in args.items() if k != "self"}
        code = code_gen_func(to_json(args_type(**args)))
        result_json = self._driver.execute_script(code)
        return ProcessPageResult.from_json(result_json)


class DomSnapshotScriptGeneric(DomSnapshotScript):
    _script_code = resource.get_resource("processPagePoll.js")
    _poll_result_code = resource.get_resource("pollResult.js")

    def process_page_script_code(self, args):
        # type: (Text) -> Text
        return "{} return __processPagePoll({});".format(self._script_code, args)

    def poll_result_script_code(self, args):
        # type: (Text) -> Text
        return "{} return __pollResult({});".format(self._poll_result_code, args)


class DomSnapshotScriptForIE(DomSnapshotScript):
    _script_code = resource.get_resource("processPagePollForIE.js")
    _poll_result_code = resource.get_resource("pollResultForIE.js")

    def process_page_script_code(self, args):
        # type: (Text) -> Text
        return "{} return __processPagePollForIE({});".format(self._script_code, args)

    def poll_result_script_code(self, args):
        # type: (Text) -> Text
        return "{} return __pollResultForIE({});".format(self._poll_result_code, args)


class RecursiveSnapshotter(object):
    POLL_INTERVAL_MS = 1000

    def __init__(
        self,
        driver,  # type: EyesWebDriver
        script,  # type: DomSnapshotScript
        logger,  # type: BoundLogger
        timeout_ms,  # type: int
        chunk_byte_length,  # type: int
        cross_origin_rendering,  # type: bool
        use_cookies,  # type: bool
        **script_args  # type: Any
    ):
        self.should_skip_failed_frames = False
        self._driver = driver
        self._script = script
        self._logger = logger
        self._deadline_time = time() + datetime_utils.to_sec(timeout_ms)
        self._chunk_byte_length = chunk_byte_length
        self._cross_origin_rendering = cross_origin_rendering
        self._use_cookies = use_cookies
        self._script_args = script_args

    def create_cross_frames_dom_snapshots(self):
        dom = self._create_dom_snapshot_loop()
        self._process_dom_snapshot_frames(dom)
        return dom

    def _create_dom_snapshot_loop(self):
        # type: () -> Dict
        chunks = []
        result = self._script.run(**self._script_args)
        while result.status is ProcessPageStatus.WIP or (
            result.status is ProcessPageStatus.SUCCESS_CHUNKED and not result.done
        ):
            if time() > self._deadline_time:
                raise DomSnapshotTimeout
            result = self._script.poll_result(self._chunk_byte_length)
            if result.status is ProcessPageStatus.WIP:
                datetime_utils.sleep(
                    self.POLL_INTERVAL_MS,
                    "Waiting for the end of DOM extraction",
                )
            elif result.status is ProcessPageStatus.SUCCESS_CHUNKED:
                self._logger.info(
                    "Snapshot chunk {}, {}B".format(len(chunks), len(result.value))
                )
                chunks.append(result.value)
        if result.status is ProcessPageStatus.SUCCESS:
            return result.value
        elif result.status.SUCCESS_CHUNKED and result.done:
            return json.loads("".join(chunks))
        elif result.status is ProcessPageStatus.ERROR:
            raise DomSnapshotScriptError(result.error)
        else:
            raise DomSnapshotFailure("Unexpected script result", result)

    def _process_dom_snapshot_frames(self, dom):
        # type: (Dict) -> None
        if self._use_cookies:
            dom["cookies"] = self._driver.get_cookies()
        for frame in dom["frames"]:
            selector = frame.get("selector", None)
            if not selector:
                self._logger.warning("inner frame with null selector")
                continue
            try:
                with self._driver.switch_to.frame_and_back(
                    FrameLocator(frame_selector=[By.CSS_SELECTOR, selector])
                ):
                    self._process_dom_snapshot_frames(frame)
            except Exception:
                if self.should_skip_failed_frames:
                    self._logger.warning(
                        "failed switching to frame",
                        frame_selector=selector,
                        exc_info=True,
                    )
                else:
                    raise
        if self._cross_origin_rendering:
            self._snapshot_and_process_cors_frames(dom)

    def _snapshot_and_process_cors_frames(self, dom):
        # type: (Dict) -> None
        for frame in dom["crossFrames"]:
            selector = frame.get("selector", None)
            if not selector:
                self._logger.warning("cross frame with null selector")
                continue
            frame_index = frame["index"]
            try:
                with self._driver.switch_to.frame_and_back(
                    FrameLocator(frame_selector=[By.CSS_SELECTOR, selector])
                ):
                    frame_dom = self.create_cross_frames_dom_snapshots()
                    dom.setdefault("frames", []).append(frame_dom)
                    frame_url = frame_dom["url"]
                    dom["cdt"][frame_index]["attributes"].append(
                        {"name": "data-applitools-src", "value": frame_url}
                    )
                    self._logger.info(
                        "Created cross origin frame snapshot {}".format(frame_url)
                    )
                    self._process_dom_snapshot_frames(frame_dom)
            except Exception:
                if self.should_skip_failed_frames:
                    self._logger.warning(
                        "failed extracting and processing cross frame",
                        frame_selector=selector,
                        exc_info=True,
                    )
                else:
                    raise


def has_cross_subframes(dom):
    if dom["crossFrames"]:
        return True
    return any(has_cross_subframes(frame) for frame in dom["frames"])
