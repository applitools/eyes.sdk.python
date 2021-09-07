from __future__ import absolute_import, unicode_literals

from typing import TYPE_CHECKING, Optional, Text, Union

from robot.libraries.BuiltIn import BuiltIn

from applitools.common import BatchInfo, MatchLevel, TestResults, TestResultsSummary
from applitools.selenium import Eyes, EyesWebDriver

from ..base import LibraryComponent, keyword
from ..utils import parse_viewport_size
from .keyword_tags import CHECK_FLOW


class RunnerKeywords(LibraryComponent):
    @keyword("Eyes Create Runner")
    def create_runner(self, type):
        self._create_eyes_runner_if_needed()

    @keyword("Eyes Get All Test Results")
    def get_all_tests_results(self):
        # type: () -> TestResultsSummary
        results = self.eyes_runner.get_all_test_results()
        self.info("Running tests result: {}".format(results))
        return results


class SessionKeywords(LibraryComponent):
    @keyword(
        "Eyes Open",
        types={
            "app_name": (str, None),
            "test_name": (str, None),
            "viewport_size": (str, None),
            "host_os": (str, None),
            "host_app": (str, None),
            "match_level": (str, None),
            "batch": (str, BatchInfo, None),
            "baseline_env_name": (str, None),
            "hide_scrollbars": (bool, None),
            "stitch_mode": (str, None),
            "force_full_page_screenshot": (bool, None),
            "match_timeout": (int, None),
            "save_new_tests": (bool, None),
            "wait_before_screenshots": (bool, None),
            "send_dom": (bool, None),
            "is_disabled": (bool, None),
        },
        tags=(CHECK_FLOW,),
    )
    def open(  # noqa
        self,
        test_name=None,  # type: Optional[Text]
        viewport_size=None,  # type: Optional[int]
        app_name=None,  # type: Optional[Text]
        host_os=None,  # type: Optional[Text]
        host_app=None,  # type: Optional[Text]
        match_level=None,  # type: Optional[Text]
        baseline_env_name=None,  # type: Optional[Text]
        batch=None,  # type: Optional[Union[BatchInfo,Text]]
        branch_name=None,  # type: Optional[Text]
        parent_branch_name=None,  # type: Optional[Text]
        force_full_page_screenshot=None,  # type: Optional[bool]
        stitch_mode=None,  # type: Optional[Text]
        match_timeout=None,  # type: Optional[int]
        hide_scrollbars=None,  # type: Optional[bool]
        save_new_tests=None,  # type: Optional[bool]
        wait_before_screenshots=None,  # type: Optional[bool]
        send_dom=None,  # type: Optional[bool]
        is_disabled=None,  # type: Optional[bool]
    ):
        # type: (...)->EyesWebDriver
        """
        Shared parameters section from `applitools.yaml` could be overwritten during Open call, see `Preconditions`.
            | =Arguments=                  | =Description=                                                                                                                               |
            | Test Name                    | By default fetched from name of current test. Could be overfritet here.                                                                     |
            | Viewport Size                | The viewport size of the browser window in format [width height] e.g. [1900 1080]                                                           |
            | App Name                     | The name of the application under test                                                                                                      |
            | Host OS                      | The operating system of the test, can be used to override the OS name to allow cross OS verification                                        |
            | Host App                     | The browser name for the test, can be used to override the browser name to allow cross browser verification                                 |
            | Match Level                  | The match level for the comparison of this test's checkpoints - can be STRICT, LAYOUT, CONTENT or EXACT                                     |
            | Baseline Env Name            | Name of the branch where the baseline reference will be taken from and where new and accepted steps will be saved to                        |
            | Batch                        | The desired batch. See `Group tests into batches`                                                                                           |
            | Branch Name                  | The branch to use to check test                                                                                                             |
            | Parent Branch Name           | Parent Branch to base the new Branch on                                                                                                     |
            | Force Full Page Screenshot   | Will force the browser to take a screenshot of whole page                                                                                   |
            | Stitch Mode                  | Type of stitching used for full page screenshots - can be CSS or SCROLL                                                                     |
            | Match Timeout                | Determines how much time in milliseconds Eyes continues to retry the matching before declaring a mismatch on this test checkpoints          |
            | Hide Scrollbars              | Sets if the scrollbars are hidden this session's tests, by passing 'True' or 'False' in the variable                                        |
            | Save New Tests               | Sets if the new checkpoints on this session are automatically accepted, by passing 'True' or 'False' in the variable                        |
            | Wait Before Screenshots      | Determines the number of milliseconds that Eyes will wait before capturing a screenshot on this test checkpoints                            |
            | Send DOM                     | Sets if DOM information should be sent for this session's checkpoints                                                                       |
            | Stitch Content               | If this test checkpoint's elements/region are scrollable, determines if Eyes will scroll this them to take a full region/element screenshot |
            | Is Disabled                  | Determines whether or not interactions with Eyes will be silently ignored for this test                                                     |

        When opening the session on a mobile browser or hybrid app, the context must be set to WEBVIEW in order to retrieve the correct viewport size. Geolocation of the device may have to be set after switching context.
        *Example:*
            | Eyes Open | TestName | [1024 768] | AppNameOverride | OSOverride | HostAppOverride | batchname=Some batch name |
        """
        config_cloned = self.get_configuration()
        if app_name:
            config_cloned.app_name = app_name
        elif config_cloned.app_name is None:
            raise ValueError("app_name should be provided")

        if test_name:
            config_cloned.test_name = test_name
        elif config_cloned.test_name is None:
            # no test_name present use test name from the suite
            config_cloned.test_name = BuiltIn().get_variable_value("${TEST NAME}")

        if batch:
            if isinstance(batch, str):
                batch = BatchInfo(name=batch)
            if isinstance(batch, BatchInfo):
                config_cloned.batch = batch
            else:
                raise TypeError("No proper value for BatchInfo")

        if viewport_size:
            config_cloned.viewport_size = parse_viewport_size(viewport_size)

        if host_os:
            config_cloned.host_os = host_os
        if host_app:
            config_cloned.host_app = host_app
        if match_level:
            config_cloned.match_level = MatchLevel(match_level)
        if baseline_env_name:
            config_cloned.baseline_env_name = baseline_env_name
        if branch_name:
            config_cloned.branch_name = branch_name
        if parent_branch_name:
            config_cloned.parent_branch_name = parent_branch_name
        if force_full_page_screenshot:
            config_cloned.force_full_page_screenshot = force_full_page_screenshot
        if stitch_mode:
            config_cloned.stitch_mode = stitch_mode
        if match_timeout:
            config_cloned.match_timeout = match_timeout
        if hide_scrollbars:
            config_cloned.hide_scrollbars = hide_scrollbars
        if save_new_tests:
            config_cloned.save_new_tests = save_new_tests
        if wait_before_screenshots:
            config_cloned.wait_before_screenshots = wait_before_screenshots
        if send_dom:
            config_cloned.send_dom = send_dom
        if is_disabled:
            config_cloned.is_disabled = is_disabled

        eyes = Eyes(self.eyes_runner)
        eyes.set_configuration(config_cloned)
        self.register_eyes(eyes)
        return eyes.open(self.fetch_driver())

    @keyword(
        "Eyes Close Async",
        types=(bool,),
        tags=(CHECK_FLOW,),
    )
    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Closes a session and returns the results of the session.
        If a test is running, aborts it. Otherwise, does nothing.
            | =Arguments=                  | =Description=                                                                                                           |
            | Raise Exception (bool)       | If you don't want an exception to be thrown if there are new, missing or mismatched steps, pass 'False' in the variable |
        *Example:*
            | Eyes Close Async | ${false} |
        """
        # TODO: proper handle situation when we ask to raise an exception
        return self.current_eyes.close_async()

    @keyword(
        "Eyes Abort Async",
        tags=(CHECK_FLOW,),
    )
    def abort(self):
        # type: () -> Optional[TestResults]
        """
        Stops execution without calling close().
        This method does all the cleanup normally done by close.
        If this method is called, and close has not been called, then the test will
        have a status of Aborted in the Test Manager.

        *Example:*
            | Eyes Abort Async |
        """
        return self.current_eyes.abort_async()

    @keyword("Is Eyes Open")
    def is_open(self):
        # type: () -> bool
        """
        Returns True if Eyes is opened

        *Example:*
            | ${is_open}= | Is Eyes Open |
        """
        if self.current_eyes:
            return self.current_eyes.is_open
        return False