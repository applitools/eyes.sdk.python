import subprocess
from os import path
from textwrap import dedent


def run_robot(*args):
    test_dir = path.join(path.dirname(__file__), "resources")
    call_args = ("python", "-m", "robot") + args
    result = subprocess.run(
        call_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=test_dir
    )
    return result.returncode, result.stdout.decode()


def test_single_suite_classic_runner():
    code, output = run_robot("--variable", "RUNNER:web", "web.robot")
    expected = (
        dedent(
            """
        [ WARN ] No `config` set. Trying to find `applitools.yaml` in current path
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
        Web                                                                   | PASS |
        8 tests, 8 passed, 0 failed
        ==============================================================================
        """
        )
        .strip()
        .splitlines()
    )
    assert output.splitlines()[:-3] == expected
