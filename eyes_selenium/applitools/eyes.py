from applitools.common.match import ExactMatchSettings  # noqa
from applitools.common.server import FailureReports  # noqa

from .selenium import BatchInfo, MatchLevel, logger  # noqa
from .selenium.selenium_eyes import SeleniumEyes as Eyes  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from `applitools.core` or "
    "`applitools.selenium` instead"
)
