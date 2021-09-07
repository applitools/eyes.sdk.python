from typing import Optional

import attr

from applitools.common.selenium import Configuration
from applitools.selenium import RunnerOptions


@attr.s
class RobotConfiguration(Configuration):
    runner_options = attr.ib(default=None)  # type: Optional[RunnerOptions]
