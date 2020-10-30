import json
import time
from enum import Enum
from typing import Dict, Optional, Text, Union

import attr

from applitools.common.utils import datetime_utils
from applitools.common.utils.json_utils import JsonInclude, to_json
from applitools.selenium import resource

RESPONSE_LIMIT_IOS = 10 * 1024 * 1024
RESPONSE_LIMIT_GENERIC = 256 * 1024 * 1024


class DomSnapshotFailure(Exception):
    pass


class DomSnapshotScriptError(DomSnapshotFailure):
    pass


class DomSnapshotTimeout(DomSnapshotFailure):
    def __init__(self, timeout_ms):
        super(DomSnapshotTimeout, self).__init__(
            "Dom-Snapshot polling took more than {} ms".format(timeout_ms)
        )


def create_dom_snapshot(
    driver, dont_fetch_resources, skip_resources, timeout_ms=5 * 60 * 1000
):
    is_ie = driver.user_agent.is_internet_explorer
    script_type = DomSnapshotScriptForIE if is_ie else DomSnapshotScriptGeneric
    script = script_type(driver)
    is_ios = "ios" in driver.desired_capabilities.get("platformName", "").lower()
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
        return self._run_script(
            locals(), ProcessPageArgs, self.process_page_script_code
        )

    def poll_result(self, chunk_byte_length=None):
        return self._run_script(locals(), PollResultArgs, self.poll_result_script_code)

    def _run_script(self, args, args_type, code_gen_func):
        args = {k: v for k, v in args.items() if k != "self"}
        code = code_gen_func(to_json(args_type(**args)))
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


def create_dom_snapshot_loop(
    script, timeout_ms, poll_interval_ms, chunk_byte_length, **script_args
):
    chunks = []
    deadline = time.monotonic() + timeout_ms / 1000.0
    result = script.run(**script_args)
    while result.status in (ProcessPageStatus.WIP, ProcessPageStatus.SUCCESS_CHUNKED):
        if time.monotonic() > deadline:
            raise DomSnapshotTimeout(timeout_ms)
        result = script.poll_result(chunk_byte_length)
        if result.status is ProcessPageStatus.SUCCESS_CHUNKED:
            chunks.append(result.value)
            if result.done:
                break
        datetime_utils.sleep(poll_interval_ms, "Waiting for the end of DOM extraction")
    if result.status is ProcessPageStatus.SUCCESS:
        return result.value
    elif result.status.SUCCESS_CHUNKED and result.done:
        return json.loads("".join(chunks))
    elif result.status is ProcessPageStatus.ERROR:
        raise DomSnapshotScriptError(result.error)
    else:
        raise DomSnapshotFailure("Unexpected script result", result)
