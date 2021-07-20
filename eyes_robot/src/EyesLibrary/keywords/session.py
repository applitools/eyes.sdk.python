from typing import TYPE_CHECKING, Optional, Text

from robot.libraries.BuiltIn import BuiltIn

from applitools.common.selenium import Configuration
from applitools.selenium import Eyes

from ..config import SelectedRunner

if TYPE_CHECKING:
    from applitools.selenium import EyesWebDriver
    from applitools.common import (
        TestResults,
        TestResultsSummary,
        RectangleSize,
        BatchInfo,
        MatchLevel,
    )

from ..base import LibraryComponent, keyword


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
            "width": (int, None),
            "height": (int, None),
            "host_os": (str, None),
            "host_app": (str, None),
            "match_level": (str, None),
            "batch": (str, BatchInfo, None),
            "baseline_name": (str, None),
            "hide_scrollbars": (bool, None),
            "stitch_mode": (str, None),
            "force_full_page_screenshot": (bool, None),
            "match_timeout": (int, None),
            "save_new_tests": (bool, None),
            "wait_before_screenshots": (bool, None),
            "send_dom": (bool, None),
            "is_disabled": (bool, None),
        },
    )
    def open(
        self,
        app_name=None,  # type: Optional[Text]
        test_name=None,  # type: Optional[Text]
        width=None,  # type: Optional[int]
        height=None,  # type: Optional[int]
        host_os=None,  # type: Optional[Text]
        host_app=None,  # type: Optional[Text]
        match_level=None,  # type: Optional[Text]
        baseline_env_name=None,  # type: Optional[Text]
        batch=None,  # type: Optional[Text]
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
        Open Eyes session. Some of the following arguments may also be defined on library import.
        See `Before running tests` or `Importing`.
            | =Arguments=                  | =Description=                                                                                                                               |
            | App Name                     | *Mandatory* - The name of the application under test                                                                                        |
            | Test Name                    | By default fetched from name of current test. Could be overfritet here.                                                                                                               |
            | Width                        | The width of the browser window e.g. 1920                                                                                                   |
            | Height                       | The height of the browser window e.g. 1080                                                                                                  |
            | Host OS                      | The operating system of the test, can be used to override the OS name to allow cross OS verification                                        |
            | Host App                     | The browser name for the test, can be used to override the browser name to allow cross browser verification                                 |
            | Match Level                  | The match level for the comparison of this test's checkpoints - can be STRICT, LAYOUT, CONTENT or EXACT                                     |
            | Baseline Env Name            | Name of the branch where the baseline reference will be taken from and where new and accepted steps will be saved to                        |
            | Batch (str or BatchInfo)     | The desired batch. See `Group tests into batches`                                                                                           |
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
        *Mandatory Arguments:* They may be defined through this keyword, or in configuration.yaml.
        In order to run a test, provide at least the API Key, Application Name and Test Name.

        When opening the session on a mobile browser or hybrid app, the context must be set to WEBVIEW in order to retrieve the correct viewport size. Geolocation of the device may have to be set after switching context.
        *Example:*
            | Eyes Open | AppName | TestName | 1024 | 768 | OSOverrideName | AppOverrideName | batchname=Some batch name |
        """
        # Should be called before actual open
        config = self.parse_configuration_and_initialize_runner(
            # runner=SelectedRunner(runner)
        )  # type: Configuration

        if app_name:
            config.app_name = app_name
        elif config.app_name is None:
            raise ValueError("app_name should be provided")

        if test_name:
            config.test_name = test_name
        elif config.test_name is None:
            # no test_name present use test name from the suite
            config.test_name = BuiltIn().get_variable_value("${TEST NAME}")

        if batch:
            if isinstance(batch, str):
                batch = BatchInfo(name=batch)
            if isinstance(batch, BatchInfo):
                config.batch = batch
            else:
                raise TypeError("No proper value for BatchInfo")

        if width and height:
            config.viewport_size = RectangleSize(width, height)

        if host_os:
            config.host_os = host_os
        if host_app:
            config.host_app = host_app
        if match_level:
            config.match_level = MatchLevel(match_level)
        if baseline_env_name:
            config.baseline_env_name = baseline_env_name
        if branch_name:
            config.branch_name = branch_name
        if parent_branch_name:
            config.parent_branch_name = parent_branch_name
        if force_full_page_screenshot:
            config.force_full_page_screenshot = force_full_page_screenshot
        if stitch_mode:
            config.stitch_mode = stitch_mode
        if match_timeout:
            config.match_timeout = match_timeout
        if hide_scrollbars:
            config.hide_scrollbars = hide_scrollbars
        if save_new_tests:
            config.save_new_tests = save_new_tests
        if wait_before_screenshots:
            config.wait_before_screenshots = wait_before_screenshots
        if send_dom:
            config.send_dom = send_dom
        if is_disabled:
            config.is_disabled = is_disabled

        eyes = Eyes(self.eyes_runner)
        eyes.set_configuration(config)
        self.register_eyes(eyes)
        return eyes.open(self.fetch_driver())

    @keyword("Eyes Close", types=(bool,))
    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Closes a session and returns the results of the session.
        If a test is running, aborts it. Otherwise, does nothing.
            | =Arguments=                  | =Description=                                                                                                           |
            | Raise Exception (bool)       | If you don't want an exception to be thrown if there are new, missing or mismatched steps, pass 'False' in the variable |
        *Example:*
            | Eyes Close | ${false} |
        """
        # TODO: proper handle situation when we ask to raise an exception
        return self.current_eyes.close_async()

    @keyword("Eyes Abort")
    def abort(self):
        # type: () -> Optional[TestResults]
        """
        Stops execution without calling close().
        This method does all the cleanup normally done by close.
        If this method is called, and close has not been called, then the test will
        have a status of Aborted in the Test Manager.

        *Example:*
            | Eyes Abort |
        """
        return self.current_eyes.abort_async()
