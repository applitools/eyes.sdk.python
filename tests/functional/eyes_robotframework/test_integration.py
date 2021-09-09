import subprocess
from os import path
from textwrap import dedent


def run_robot(*args):
    test_dir = path.join(path.dirname(__file__), "robot_tests")
    call_args = ("python", "-m", "robot") + args
    result = subprocess.run(
        call_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=test_dir
    )
    return result.returncode, result.stdout.decode()


def lines(text):
    return [line.strip() for line in dedent(text).strip().splitlines()]


def test_single_suite_classic_runner():
    expected = lines(
        """
        [ WARN ] No `config` set. Trying to find `applitools.yaml` in current path
        Runing test suite with `web` runner and `applitools.yaml` config
        Using library `SeleniumLibrary` as backend
        ==============================================================================
        Web
        ==============================================================================
        Check Window                                                          | PASS |
        ------------------------------------------------------------------------------
        Check Window Fully                                                    | PASS |
        ------------------------------------------------------------------------------
        Eyes Open Close Multiple Times                                        | PASS |
        ------------------------------------------------------------------------------
        Check Region By Element                                               | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector                                              | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector With Ignore                                  | PASS |
        ------------------------------------------------------------------------------
        Check Window Two Times                                                | PASS |
        ------------------------------------------------------------------------------
        Check Region By Coordinates In Frame                                  | PASS |
        ------------------------------------------------------------------------------
        """
    )
    code, output = run_robot(
        "--variable",
        "RUNNER:web",
        "web.robot",
    )
    assert lines(output)[: len(expected)] == expected


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
        Runing test suite with `web` runner and `../applitools.yaml` config
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
    assert code == 0


def test_suite_ufg_runner():
    code, output = run_robot(
        "--variablefile",
        "variables_test.py:web_ufg:selenium:desktop",
        "web_only.robot",
    )
    expected = lines(
        """
        [ WARN ] No `config` set. Trying to find `applitools.yaml` in current path
        Runing test suite with `web_ufg` runner and `applitools.yaml` config
        Using library `SeleniumLibrary` as backend
        ==============================================================================
        Web Only
        ==============================================================================
        Check Window                                                          | PASS |
        ------------------------------------------------------------------------------
        Check Window Fully                                                    | PASS |
        ------------------------------------------------------------------------------
        Eyes Open Close Multiple Times                                        | PASS |
        ------------------------------------------------------------------------------
        Check Region By Element                                               | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector                                              | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector With Ignore                                  | PASS |
        ------------------------------------------------------------------------------
        Check Window Two Times                                                | PASS |
        ------------------------------------------------------------------------------
        Check Region By Coordinates In Frame                                  | PASS |
        ------------------------------------------------------------------------------
        """
    )
    assert lines(output)[: len(expected)] == expected
    assert code == 0


def test_suite_classic_appium_ios_runner():
    code, output = run_robot(
        "--variablefile",
        "variables_test.py:web:appium:ios",
        "web_only.robot",
    )
    expected = lines(
        """
        [ WARN ] No `config` set. Trying to find `applitools.yaml` in current path
        Runing test suite with `web_ufg` runner and `applitools.yaml` config
        Using library `SeleniumLibrary` as backend
        ==============================================================================
        Web Only
        ==============================================================================
        Check Window                                                          | PASS |
        ------------------------------------------------------------------------------
        Check Window Fully                                                    | PASS |
        ------------------------------------------------------------------------------
        Eyes Open Close Multiple Times                                        | PASS |
        ------------------------------------------------------------------------------
        Check Region By Element                                               | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector                                              | PASS |
        ------------------------------------------------------------------------------
        Check Region By Selector With Ignore                                  | PASS |
        ------------------------------------------------------------------------------
        Check Window Two Times                                                | PASS |
        ------------------------------------------------------------------------------
        Check Region By Coordinates In Frame                                  | PASS |
        ------------------------------------------------------------------------------
        """
    )
    assert lines(output)[: len(expected)] == expected
    assert code == 0
