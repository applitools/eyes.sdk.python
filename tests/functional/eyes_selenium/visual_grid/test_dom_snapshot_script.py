import base64
import json
import zlib
from time import sleep, time
from typing import Text

import mock
import pytest

from applitools.selenium import EyesWebDriver
from applitools.selenium.visual_grid import dom_snapshot_script
from applitools.selenium.visual_grid.dom_snapshot_script import (
    DomSnapshotScript,
    DomSnapshotScriptError,
    DomSnapshotScriptForIE,
    DomSnapshotScriptGeneric,
    DomSnapshotTimeout,
    ProcessPageResult,
    ProcessPageStatus,
    create_dom_snapshot,
    create_dom_snapshot_loop,
    has_cross_subframes,
)

picture_url = (
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/minions-300x188.jpg"
)


def test_dom_snapshot_args_conversion():
    class DomSnapshotScriptMock(DomSnapshotScript):
        def process_page_script_code(self, args):
            self.run_args = args
            return ""

        def poll_result_script_code(self, args):
            self.poll_args = args
            return ""

    driver = mock.MagicMock()
    driver.execute_script.return_value = '{"status": "WIP"}'
    script = DomSnapshotScriptMock(driver)

    script.run(
        show_logs=False,
        use_session_cache=True,
        dont_fetch_resources=True,
        fetch_timeout=10,
        skip_resources=["http://a.com"],
        compress_resources=True,
        serialize_resources=True,
    )
    script.poll_result(chunk_byte_length=100)

    assert json.loads(script.run_args) == {
        "compressResources": True,
        "dontFetchResources": True,
        "fetchTimeout": 10,
        "serializeResources": True,
        "showLogs": False,
        "skipResources": ["http://a.com"],
        "useSessionCache": True,
    }
    assert json.loads(script.poll_args) == {"chunkByteLength": 100}


def test_dom_snapshot_default(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run()
    for _ in range(10):
        poll_res = script.poll_result()
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS
    assert poll_res.value["resourceUrls"] == []
    assert len(poll_res.value["blobs"][0]["value"]) == 0
    assert "compressed" not in poll_res.value["blobs"][0]


def test_dom_snapshot_serialize_resources(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run(serialize_resources=True)
    for _ in range(10):
        poll_res = script.poll_result()
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS
    assert poll_res.value["resourceUrls"] == []
    assert len(poll_res.value["blobs"][0]["value"]) == 30296
    assert "compressed" not in poll_res.value["blobs"][0]
    pic = base64.b64decode(poll_res.value["blobs"][0]["value"])
    assert len(pic) == 22721


def test_dom_snapshot_compressed(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run(compress_resources=True)
    for _ in range(10):
        poll_res = script.poll_result()
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS
    assert poll_res.value["resourceUrls"] == []
    assert poll_res.value["blobs"][0]["compressed"] is True
    assert len(poll_res.value["blobs"][0]["value"]) == 21674
    compressed_dict = poll_res.value["blobs"][0]["value"]
    compressed = bytearray(compressed_dict[str(i)] for i in range(len(compressed_dict)))
    pic = zlib.decompress(bytes(compressed))
    assert len(pic) == 22721


def test_dom_snapshot_compressed_serialized(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run(compress_resources=True, serialize_resources=True)
    for _ in range(10):
        poll_res = script.poll_result()
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS
    assert poll_res.value["resourceUrls"] == []
    assert poll_res.value["blobs"][0]["compressed"] is True
    assert len(poll_res.value["blobs"][0]["value"]) == 28900
    serialized = poll_res.value["blobs"][0]["value"]
    compressed = base64.b64decode(serialized)
    pic = zlib.decompress(compressed)
    assert len(pic) == 22721


def test_dom_snapshot_dont_fetch_resources(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run(dont_fetch_resources=True)
    for _ in range(10):
        poll_res = script.poll_result()
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS
    assert poll_res.value["blobs"] == []
    assert poll_res.value["resourceUrls"] == [picture_url]


def test_dom_snapshot_serialize_chunks(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run(serialize_resources=True)
    for _ in range(10):
        poll_res = script.poll_result(chunk_byte_length=100)
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS_CHUNKED
    assert poll_res.done is False
    assert type(poll_res.value) is Text
    assert len(poll_res.value) == 100


def test_dom_snapshot_serialize_chunks_until_done(driver):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    script = DomSnapshotScriptGeneric(driver)

    run_res = script.run(serialize_resources=True)
    while True:
        poll_res = script.poll_result(chunk_byte_length=2 ** 15)
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    while True:
        poll_res = script.poll_result(chunk_byte_length=2 ** 15)
        if poll_res.status is ProcessPageStatus.WIP:
            sleep(1)
        else:
            break

    assert run_res == ProcessPageResult(ProcessPageStatus.WIP)
    assert poll_res.status == ProcessPageStatus.SUCCESS_CHUNKED
    assert poll_res.done is True
    assert type(poll_res.value) is Text
    assert len(poll_res.value) == 7245


@pytest.fixture
def mocked_create_dom_snapshot_loop():
    with mock.patch(
        "applitools.selenium.visual_grid.dom_snapshot_script.create_dom_snapshot_loop"
    ) as patched:
        yield patched


def test_create_dom_snapshot_ie(mocked_create_dom_snapshot_loop):
    driver = mock.MagicMock()
    driver.user_agent.is_internet_explorer = True
    create_dom_snapshot(driver, False, [], 1, True)

    calls = mocked_create_dom_snapshot_loop.call_args_list
    assert calls == [
        mock.call(
            mock.ANY,
            mock.ANY,
            1000,
            52428800,
            dont_fetch_resources=False,
            skip_resources=[],
            serialize_resources=True,
        )
    ]
    assert type(calls[0].args[0]) is DomSnapshotScriptForIE


def test_create_dom_snapshot_generic(mocked_create_dom_snapshot_loop):
    driver = mock.MagicMock()
    driver.user_agent.is_internet_explorer = False

    with mock.patch.object(dom_snapshot_script, "time", return_value=1.0) as time_mock:
        create_dom_snapshot(driver, True, [""], 1, True)

    calls = mocked_create_dom_snapshot_loop.call_args_list
    assert calls == [
        mock.call(
            mock.ANY,
            1.001,
            1000,
            52428800,
            dont_fetch_resources=True,
            skip_resources=[""],
            serialize_resources=True,
        )
    ]
    assert type(calls[0].args[0]) is DomSnapshotScriptGeneric


def test_create_dom_snapshot_ios(mocked_create_dom_snapshot_loop):
    driver = mock.MagicMock()
    driver.user_agent.is_internet_explorer = False
    driver.desired_capabilities = {"platformName": "ios"}
    create_dom_snapshot(driver, True, [], 1, True)

    calls = mocked_create_dom_snapshot_loop.call_args_list
    assert calls == [
        mock.call(
            mock.ANY,
            mock.ANY,
            1000,
            10485760,
            dont_fetch_resources=True,
            skip_resources=[],
            serialize_resources=True,
        )
    ]
    assert type(calls[0].args[0]) is DomSnapshotScriptGeneric


def test_create_dom_snapshot_loop_timeout():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.return_value = ProcessPageResult(ProcessPageStatus.WIP)

    with pytest.raises(DomSnapshotTimeout):
        create_dom_snapshot_loop(script, 5, 2, 3)


def test_create_dom_snapshot_loop_calls_run_with_args():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.return_value = ProcessPageResult(
        ProcessPageStatus.SUCCESS, value={}
    )

    create_dom_snapshot_loop(
        script, time() + 1, 2, 3, dont_fetch_resources=True, skip_resources=[]
    )

    calls = script.run.call_args_list
    assert calls == [mock.call(dont_fetch_resources=True, skip_resources=[])]


def test_create_dom_snapshot_loop_calls_poll_result():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.return_value = ProcessPageResult(
        ProcessPageStatus.SUCCESS, value={}
    )

    create_dom_snapshot_loop(script, time() + 1, 2, 3)

    calls = script.poll_result.call_args_list
    assert calls == [mock.call(3)]


def test_create_dom_snapshot_loop_calls_poll_result_with_chunk_byte_length():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.return_value = ProcessPageResult(
        ProcessPageStatus.SUCCESS, value={}
    )

    create_dom_snapshot_loop(script, time() + 1, 2, 3)

    calls = script.poll_result.call_args_list
    assert calls == [mock.call(3)]


def test_create_dom_snapshot_loop_raises_if_run_returns_error():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.ERROR, error="OOPS")

    with pytest.raises(DomSnapshotScriptError, match="OOPS"):
        create_dom_snapshot_loop(script, 1, 2, 3)


def test_create_dom_snapshot_loop_raises_if_poll_result_returns_error():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.return_value = ProcessPageResult(
        ProcessPageStatus.ERROR, error="OOPS"
    )

    with pytest.raises(DomSnapshotScriptError, match="OOPS"):
        create_dom_snapshot_loop(script, time() + 10, 2, 3)


def test_create_dom_snapshot_loop_success():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.return_value = ProcessPageResult(
        ProcessPageStatus.SUCCESS, value={"a": "b"}
    )

    res = create_dom_snapshot_loop(script, time() + 1, 2, 3)

    assert res == {"a": "b"}


def test_create_dom_snapshot_loop_chunks():
    script = mock.MagicMock()
    script.run.return_value = ProcessPageResult(ProcessPageStatus.WIP)
    script.poll_result.side_effect = [
        ProcessPageResult(ProcessPageStatus.SUCCESS_CHUNKED, done=False, value='{"a"'),
        ProcessPageResult(ProcessPageStatus.SUCCESS_CHUNKED, done=True, value=':"b"}'),
    ]

    res = create_dom_snapshot_loop(script, time() + 1, 1, 3)

    assert res == {"a": "b"}


def test_create_dom_snapshot_with_cors_iframe(driver):
    driver = EyesWebDriver(driver, None)
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/")

    dom = create_dom_snapshot(driver, False, [], 10000, True)

    assert len(dom["frames"][0]["crossFrames"]) == 1
    assert dom["frames"][0]["crossFrames"][0]["index"] == 16
    assert "selector" in dom["frames"][0]["crossFrames"][0]


def test_create_dom_snapshot_has_cors_iframe_data(driver):
    driver = EyesWebDriver(driver, None)
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/")

    dom = create_dom_snapshot(driver, False, [], 10000, True)

    assert len(dom["frames"][0]["frames"]) == 1
    assert (
        dom["frames"][0]["frames"][0]["url"]
        == "https://afternoon-savannah-68940.herokuapp.com/#"
    )


def test_has_cross_sub_frames_one_level_empty():
    dom = {"frames": [], "crossFrames": []}

    assert has_cross_subframes(dom) is False


def test_has_cross_sub_frames_one_level():
    dom = {"frames": [], "crossFrames": [{}]}

    assert has_cross_subframes(dom) is True


def test_has_cross_sub_frames_two_level():
    dom = {"frames": [{"frames": [], "crossFrames": [{}]}], "crossFrames": []}

    assert has_cross_subframes(dom) is True


def test_has_cross_sub_frames_two_level_empty():
    dom = {
        "frames": [{"frames": [{"frames": [], "crossFrames": []}], "crossFrames": []}],
        "crossFrames": [],
    }

    assert has_cross_subframes(dom) is False


def test_create_dom_snapshot_disable_cross_origin_rendering(driver):
    driver = EyesWebDriver(driver, None)
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/")

    dom = create_dom_snapshot(driver, False, [], 10000, False)

    assert len(dom["frames"][0]["frames"]) == 0


def test_create_dom_snapshot_retries_on_single_failure(driver, monkeypatch):
    create_dom_snapshot_loop = dom_snapshot_script.create_dom_snapshot_loop

    def failing_once_loop(*args, **kwargs):
        failing_once_loop.call_count += 1
        if failing_once_loop.call_count == 2:
            raise Exception
        else:
            return create_dom_snapshot_loop(*args, **kwargs)

    failing_once_loop.call_count = 0
    monkeypatch.setattr(
        dom_snapshot_script, "create_dom_snapshot_loop", failing_once_loop
    )

    driver = EyesWebDriver(driver, None)
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/")

    dom = create_dom_snapshot(driver, False, [], 1000000, True)

    assert len(dom["frames"][0]["crossFrames"]) == 1
    assert dom["frames"][0]["crossFrames"][0]["index"] == 16
    assert "selector" in dom["frames"][0]["crossFrames"][0]
