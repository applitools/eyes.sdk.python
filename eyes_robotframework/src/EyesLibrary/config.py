from typing import Optional

import attr

from applitools.common.selenium import Configuration


@attr.s
class RobotRunnerOptions(object):
    test_concurrency = attr.ib(default=None)  # type: Optional[int]
    dont_close_batches = attr.ib(default=None)  # type: Optional[bool]


@attr.s
class RobotConfiguration(Configuration):
    runner_options = attr.ib(default=None)  # type: Optional[RobotRunnerOptions]
