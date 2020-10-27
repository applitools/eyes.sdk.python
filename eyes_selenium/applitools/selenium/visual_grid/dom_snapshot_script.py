import json
import time
from enum import Enum
from typing import Dict, Optional, Text, Union

import attr

from applitools.common.utils import datetime_utils
from applitools.common.utils.json_utils import JsonInclude, to_json
from applitools.selenium import resource

RESPONSE_LIMIT_IOS = 10 * 1024 * 1024
RESPONSE_LIMIT_GENERIC = 1 * 1024 * 1024


class DomSnapshotFailure(Exception):
    pass


class DomSnapshotTimeout(DomSnapshotFailure):
    def __init__(self, timeout_ms):
        super(DomSnapshotTimeout, self).__init__(
            "Dom-Snapshot polling took more than {} ms".format(timeout_ms)
        )


class DomSnapshotScriptError(DomSnapshotFailure):
    @classmethod
    def check(cls, process_page_result):
        if process_page_result.status is ProcessPageStatus.ERROR:
            raise cls(process_page_result.error)


@attr.s
class ProcessPageArgs(object):
    show_logs = attr.ib(type=bool, metadata={JsonInclude.NON_NONE: True})
    use_session_cache = attr.ib(type=bool, metadata={JsonInclude.NON_NONE: True})
    dont_fetch_resources = attr.ib(type=bool, metadata={JsonInclude.NON_NONE: True})
    fetch_timeout = attr.ib(type=int, metadata={JsonInclude.NON_NONE: True})
    skip_resources = attr.ib(type=list, metadata={JsonInclude.NON_NONE: True})
    compress_resources = attr.ib(type=bool, metadata={JsonInclude.NON_NONE: True})
    serialize_resources = attr.ib(type=bool, metadata={JsonInclude.NON_NONE: True})


@attr.s
class PollResultArgs(object):
    chunk_byte_length = attr.ib(type=int, metadata={JsonInclude.NON_NONE: True})


class ProcessPageStatus(Enum):
    SUCCESS = "SUCCESS"
    WIP = "WIP"
    ERROR = "ERROR"
    SUCCESS_CHUNKED = "SUCCESS_CHUNKED"


@attr.s
class ProcessPageResult(object):
    status = attr.ib(type=ProcessPageStatus)  # type: Text
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


class DomSnapshotScript(object):
    def process_page_script_code(self, args):
        raise NotImplementedError

    def poll_result_script_code(self):
        raise NotImplementedError

    def __init__(self, driver):
        self._driver = driver

    def run(
        self,
        show_logs=None,
        use_session_cache=None,
        dont_fetch_resources=None,
        fetch_timeout=None,
        skip_resources=None,
        compress_resources=None,
        serialize_resources=None,
    ):
        args = {k: v for k, v in locals().items() if k != "self"}
        arguments = ProcessPageArgs(**args)
        code = self.process_page_script_code(to_json(arguments))
        result_json = self._driver.execute_script(code)
        return ProcessPageResult.from_json(result_json)

    def poll_result(self, chunk_byte_length=None):
        args = {k: v for k, v in locals().items() if k != "self"}
        arguments = PollResultArgs(**args)
        code = self.poll_result_script_code(to_json(arguments))
        result_json = self._driver.execute_script(code)
        return ProcessPageResult.from_json(result_json)


class DomSnapshotScriptGeneric(DomSnapshotScript):
    _script_code = resource.get_resource("processPagePoll.js")
    _poll_result_code = resource.get_resource("pollResult.js")

    def process_page_script_code(self, args):
        return "{} return __processPagePoll({});".format(self._script_code, args)

    def poll_result_script_code(self, args):
        return "{} return __pollResult({});".format(self._poll_result_code, args)


class DomSnapshotScriptForIE(DomSnapshotScript):
    _script_code = resource.get_resource("processPagePollForIE.js")
    _poll_result_code = resource.get_resource("pollResultForIE.js")

    def process_page_script_code(self, args):
        return "{} return __processPagePollForIE({});".format(self._script_code, args)

    def poll_result_script_code(self, args):
        return "{} return __pollResultForIE({});".format(self._poll_result_code, args)


def create_dom_snapshot(
    driver, dont_fetch_resources, skip_resources, timeout_ms=5 * 60 * 1000
):
    is_ie = driver.user_agent.is_internet_explorer
    script_type = DomSnapshotScriptForIE if is_ie else DomSnapshotScriptGeneric
    script = script_type(driver)
    is_ios = "ios" in driver.desired_capabilities.get("platformName")
    chunk_byte_length = RESPONSE_LIMIT_IOS if is_ios else RESPONSE_LIMIT_GENERIC
    return create_dom_snapshot_loop(
        script,
        timeout_ms,
        1000,
        chunk_byte_length,
        dont_fetch_resources=dont_fetch_resources,
        skip_resources=skip_resources,
        serialize_resources=True,
    )


def create_dom_snapshot_loop(
    script, timeout_ms, poll_interval_ms, chunk_byte_length, **script_args
):
    chunks = []
    deadline = time.monotonic() + timeout_ms / 1000.0
    result = script.run(**script_args)
    DomSnapshotScriptError.check(result)
    while result.status in (ProcessPageStatus.WIP, ProcessPageStatus.SUCCESS_CHUNKED):
        if time.monotonic() > deadline:
            raise DomSnapshotTimeout(timeout_ms)
        result = script.poll_result(chunk_byte_length)
        if result.status is ProcessPageStatus.SUCCESS:
            return result.value
        elif result.status is ProcessPageStatus.SUCCESS_CHUNKED:
            chunks.append(result.value)
            if result.done:
                return json.loads("".join(chunks))
        datetime_utils.sleep(poll_interval_ms, "Waiting for the end of DOM extraction")
    DomSnapshotScriptError.check(result)
    raise DomSnapshotFailure("Unexpected script result", result)
