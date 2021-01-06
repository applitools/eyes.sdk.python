from __future__ import unicode_literals

import json
import typing
from abc import abstractmethod
from enum import Enum
from time import time

import attr
from selenium.webdriver.common.by import By

from applitools.common import logger
from applitools.common.utils import ABC, datetime_utils
from applitools.common.utils.json_utils import JsonInclude, to_json
from applitools.selenium import resource
from applitools.selenium.fluent import FrameLocator

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Text, Union

    from applitools.selenium import EyesWebDriver
    from applitools.selenium.webdriver import _EyesSwitchTo

MAX_CHUNK_BYTES_IOS = 10 * 1024 * 1024
MAX_CHUNK_BYTES_GENERIC = 50 * 1024 * 1024
SCRIPT_POLL_INTERVAL_MS = 1000


class DomSnapshotFailure(Exception):
    pass


class DomSnapshotScriptError(DomSnapshotFailure):
    pass


class DomSnapshotTimeout(DomSnapshotFailure):
    pass


def create_dom_snapshot(
    driver,
    dont_fetch_resources,
    skip_resources,
    timeout_ms,
    cross_origin_rendering,
):
    # type: (EyesWebDriver, bool, List[Text], int, bool) -> Dict
    is_ie = driver.user_agent.is_internet_explorer
    script_type = DomSnapshotScriptForIE if is_ie else DomSnapshotScriptGeneric
    script = script_type(driver)
    is_ios = "ios" in driver.desired_capabilities.get("platformName", "").lower()
    chunk_byte_length = MAX_CHUNK_BYTES_IOS if is_ios else MAX_CHUNK_BYTES_GENERIC
    deadline = time() + datetime_utils.to_sec(timeout_ms)
    try:
        return create_cross_frames_dom_snapshots(
            driver.switch_to,
            script,
            deadline,
            SCRIPT_POLL_INTERVAL_MS,
            chunk_byte_length,
            cross_origin_rendering,
            should_skip_failed_frames=False,
            dont_fetch_resources=dont_fetch_resources,
            skip_resources=skip_resources,
            serialize_resources=True,
        )
    except Exception:
        logger.info(
            "Failed to create dom-snapshot, retrying ignoring failing frames",
            exc_info=True,
        )
        return create_cross_frames_dom_snapshots(
            driver.switch_to,
            script,
            deadline,
            SCRIPT_POLL_INTERVAL_MS,
            chunk_byte_length,
            cross_origin_rendering,
            should_skip_failed_frames=True,
            dont_fetch_resources=dont_fetch_resources,
            skip_resources=skip_resources,
            serialize_resources=True,
        )


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
        # type: (Optional[bool]) -> ProcessPageResult
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


def create_dom_snapshot_loop(
    script, deadline_time, poll_interval_ms, chunk_byte_length, **script_args
):
    # type: (DomSnapshotScript, float, int, int, **Any) -> Dict
    chunks = []
    result = script.run(**script_args)
    while result.status is ProcessPageStatus.WIP or (
        result.status is ProcessPageStatus.SUCCESS_CHUNKED and not result.done
    ):
        if time() > deadline_time:
            raise DomSnapshotTimeout
        result = script.poll_result(chunk_byte_length)
        if result.status is ProcessPageStatus.WIP:
            datetime_utils.sleep(
                poll_interval_ms, "Waiting for the end of DOM extraction"
            )
        elif result.status is ProcessPageStatus.SUCCESS_CHUNKED:
            logger.info("Snapshot chunk {}, {}B".format(len(chunks), len(result.value)))
            chunks.append(result.value)
    if result.status is ProcessPageStatus.SUCCESS:
        return result.value
    elif result.status.SUCCESS_CHUNKED and result.done:
        return json.loads("".join(chunks))
    elif result.status is ProcessPageStatus.ERROR:
        raise DomSnapshotScriptError(result.error)
    else:
        raise DomSnapshotFailure("Unexpected script result", result)


def create_cross_frames_dom_snapshots(
    switch_to,  # type: _EyesSwitchTo
    script,  # type: DomSnapshotScript
    deadline_time,  # type: float
    poll_interval_ms,  # type: int
    chunk_byte_length,  # type: int
    cross_origin_rendering,  # type: bool
    should_skip_failed_frames,  # type: bool
    **script_args  # type: Any
):
    # type: (...) -> Dict
    dom = create_dom_snapshot_loop(
        script, deadline_time, poll_interval_ms, chunk_byte_length, **script_args
    )
    if cross_origin_rendering:
        process_dom_snapshot_frames(
            dom,
            switch_to,
            script,
            deadline_time,
            poll_interval_ms,
            chunk_byte_length,
            should_skip_failed_frames,
            **script_args
        )
    return dom


def process_dom_snapshot_frames(
    dom,  # type: Dict
    switch_to,  # type : _EyesSwitchTo
    script,  # type: DomSnapshotScript
    deadline_time,  # type: float
    poll_interval_ms,  # type: int
    chunk_byte_length,  # type: int
    should_skip_failed_frames,  # type: bool
    **script_args  # type: Any
):
    # type: (...) -> None
    for frame in dom["crossFrames"]:
        selector = frame.get("selector", None)
        if not selector:
            logger.warning("cross frame with null selector")
            continue
        frame_index = frame["index"]
        try:
            with switch_to.frame_and_back(
                FrameLocator(frame_selector=[By.CSS_SELECTOR, selector])
            ):
                frame_dom = create_cross_frames_dom_snapshots(
                    switch_to,
                    script,
                    deadline_time,
                    poll_interval_ms,
                    chunk_byte_length,
                    cross_origin_rendering=True,
                    should_skip_failed_frames=should_skip_failed_frames,
                    **script_args
                )
                dom.setdefault("frames", []).append(frame_dom)
                frame_url = frame_dom["url"]
                dom["cdt"][frame_index]["attributes"].append(
                    {"name": "data-applitools-src", "value": frame_url}
                )
                logger.info("Created cross origin frame snapshot {}".format(frame_url))
        except Exception:
            if should_skip_failed_frames:
                logger.warning(
                    "Failed extracting cross frame with selector {}.".format(selector),
                    exc_info=True,
                )
            else:
                raise
    for frame in dom["frames"]:
        if not has_cross_subframes(frame):
            continue
        selector = frame.get("selector", None)
        if not selector:
            logger.warning("inner frame with null selector")
            continue
        try:
            with switch_to.frame_and_back(
                FrameLocator(frame_selector=[By.CSS_SELECTOR, selector])
            ):
                process_dom_snapshot_frames(
                    frame,
                    switch_to,
                    script,
                    deadline_time,
                    poll_interval_ms,
                    chunk_byte_length,
                    should_skip_failed_frames,
                    **script_args
                )
        except Exception:
            if should_skip_failed_frames:
                logger.warning(
                    "Failed switching to frame with selector {}.".format(selector),
                    exc_info=True,
                )
            else:
                raise


def has_cross_subframes(dom):
    if dom["crossFrames"]:
        return True
    return any(has_cross_subframes(frame) for frame in dom["frames"])
