from __future__ import unicode_literals

import json
import time
import typing
from abc import abstractmethod
from enum import Enum

import attr

from applitools.common import logger
from applitools.common.utils import ABC, datetime_utils
from applitools.common.utils.json_utils import JsonInclude, to_json
from applitools.selenium import resource

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Text, Union

    from applitools.selenium import EyesWebDriver

MAX_CHUNK_BYTES_IOS = 10 * 1024 * 1024
MAX_CHUNK_BYTES_GENERIC = 256 * 1024 * 1024
SCRIPT_POLL_INTERVAL_MS = 1000


class DomSnapshotFailure(Exception):
    pass


class DomSnapshotScriptError(DomSnapshotFailure):
    pass


class DomSnapshotTimeout(DomSnapshotFailure):
    def __init__(self, timeout_ms):
        # type: (int) -> None
        super(DomSnapshotTimeout, self).__init__(
            "Dom-Snapshot polling took more than {} ms".format(timeout_ms)
        )


def create_dom_snapshot(
    driver, dont_fetch_resources, skip_resources, timeout_ms=5 * 60 * 1000
):
    # type: (EyesWebDriver, bool, List[Text], int) -> Dict
    is_ie = driver.user_agent.is_internet_explorer
    script_type = DomSnapshotScriptForIE if is_ie else DomSnapshotScriptGeneric
    script = script_type(driver)
    is_ios = "ios" in driver.desired_capabilities.get("platformName", "").lower()
    chunk_byte_length = MAX_CHUNK_BYTES_IOS if is_ios else MAX_CHUNK_BYTES_GENERIC
    return create_dom_snapshot_loop(
        script,
        timeout_ms,
        SCRIPT_POLL_INTERVAL_MS,
        chunk_byte_length,
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
    script, timeout_ms, poll_interval_ms, chunk_byte_length, **script_args
):
    # type: (DomSnapshotScript, int, int, int, **Any) -> Dict
    chunks = []
    deadline = time.time() + datetime_utils.to_sec(timeout_ms)
    result = script.run(**script_args)
    while result.status is ProcessPageStatus.WIP or (
        result.status is ProcessPageStatus.SUCCESS_CHUNKED and not result.done
    ):
        if time.time() > deadline:
            raise DomSnapshotTimeout(timeout_ms)
        result = script.poll_result(chunk_byte_length)
        if result.status is ProcessPageStatus.SUCCESS_CHUNKED:
            logger.info("Snapshot chunk {}, {}B".format(len(chunks), len(result.value)))
            chunks.append(result.value)
        datetime_utils.sleep(poll_interval_ms, "Waiting for the end of DOM extraction")
    if result.status is ProcessPageStatus.SUCCESS:
        return result.value
    elif result.status.SUCCESS_CHUNKED and result.done:
        return json.loads("".join(chunks))
    elif result.status is ProcessPageStatus.ERROR:
        raise DomSnapshotScriptError(result.error)
    else:
        raise DomSnapshotFailure("Unexpected script result", result)
