import subprocess
from os import path
from textwrap import dedent

import pytest

backend_to_backend_name = {
    "selenium": "SeleniumLibrary",
    "appium": "AppiumLibrary",
}


def run_robot(*args):
    test_dir = path.join(path.dirname(__file__), "robot_tests")
    call_args = ("python", "-m", "robot") + args
    result = subprocess.run(
        call_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=test_dir
    )
    return result.returncode, result.stdout.decode()


def lines(text):
    return [line.strip() for line in dedent(text).strip().splitlines()]


def test_suite_dir_classic_runner():
    code, output = run_robot(
        "--variable",
        "RUNNER:web",
        "test_suite_dir",
    )
    expected = lines(
        """
        ==============================================================================
        Test Suite Dir
        ==============================================================================
        Running test suite with `web` runner and `../applitools.yaml` config
        Using library `SeleniumLibrary` as backend
        Test Suite Dir.Suite1
        ==============================================================================
        Check Window Suite 1                                                  | PASS |
        ------------------------------------------------------------------------------
        Test Suite Dir.Suite1                                                 | PASS |
        1 test, 1 passed, 0 failed
        ==============================================================================
        Test Suite Dir.Suite2
        ==============================================================================
        Check Window Suite 2                                                  | PASS |
        ------------------------------------------------------------------------------
        Test Suite Dir.Suite2                                                 | PASS |
        1 test, 1 passed, 0 failed
        ==============================================================================
        Test Suite Dir.Suite3
        ==============================================================================
        Check Window Suite 3                                                  | PASS |
        ------------------------------------------------------------------------------
        """
    )
    assert lines(output)[: len(expected)] == expected
    assert code == 0, output


@pytest.mark.parametrize(
    "data",
    [
        # ("web", "selenium", "android"),
        # ("web", "appium", "ios"),
        # ("web", "selenium", "ios"),
        # ("web", "appium", "android"),
        ("web", "selenium", "desktop"),
        # ("web_ufg", "selenium", "desktop"),
    ],
    ids=lambda d: str(d),
)
def test_suite_web(data):
    runner, backend, platform = data
    code, output = run_robot(
        "--variablefile",
        "variables_test.py:{runner}:{backend}:{platform}".format(
            runner=runner, backend=backend, platform=platform
        ),
        "--output={}-{}-{}.xml".format(runner, backend, platform),
        "--log=NONE",
        "--report=NONE",
        "web_only.robot",
    )
    expected = lines(
        """
        [ WARN ] No `config` set. Trying to find `applitools.yaml` in current path
        Running test suite with `{runner}` runner and `applitools.yaml` config
        Using library `{backend_name}` as backend
        ==============================================================================
        Web Only
        ==============================================================================
        Check Window                                                          | PASS |
        ------------------------------------------------------------------------------
        Check Window Fully                                                    | PASS |
        ------------------------------------------------------------------------------
        Check Region By Element                                               | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector                                              | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector With Ignore                                  | PASS |
        ------------------------------------------------------------------------------
        Check Window Two Times                                                | PASS |
        ------------------------------------------------------------------------------
        """.format(
            runner=runner, backend_name=backend_to_backend_name[backend]
        )
    )
    assert lines(output)[: len(expected)] == expected
    assert code == 0, output


@pytest.mark.parametrize(
    "platform",
    ["android", "ios"],
    ids=lambda d: str(d),
)
def test_suite_mobile_native(platform):
    runner, backend = "mobile_native", "appium"
    code, output = run_robot(
        "--variablefile",
        "variables_test.py:{runner}:{backend}:{platform}".format(
            runner=runner, backend=backend, platform=platform
        ),
        "mobile_native.robot",
    )
    expected = lines(
        """
        [ WARN ] No `config` set. Trying to find `applitools.yaml` in current path
        Running test suite with `{runner}` runner and `applitools.yaml` config
        Using library `{backend_name}` as backend
        ==============================================================================
        Mobile Native
        ==============================================================================
        Check Window Native                                                   | PASS |
        ------------------------------------------------------------------------------
        """.format(
            runner=runner, backend_name=backend_to_backend_name[backend]
        )
    )
    assert lines(output)[: len(expected)] == expected
    assert code == 0, output
