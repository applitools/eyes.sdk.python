from __future__ import absolute_import, unicode_literals

from robot.running.model import TestSuite

from .base import LibraryComponent


class LibraryListener(LibraryComponent):
    ROBOT_LISTENER_API_VERSION = 3

    def start_suite(self, data, result):
        # type: (TestSuite, TestSuite) -> None
        self._create_eyes_runner_if_needed()
        self.debug("Runner created")

    def close(self):
        # if `Eyes Get All Test Results` was called `eyes_runner` should be set to None
        if self.ctx.eyes_runner:
            self.warn(
                "Run `Eyes Get All Test Results` keyword in `Suite Teardown` "
                "explicitly to see all output logs"
            )
            test_results = self.ctx.eyes_runner.get_all_test_results()
            self.log_to_console(test_results)
