from applitools.common.match import ExactMatchSettings  # noqa
from applitools.common.server import FailureReports  # noqa

from .selenium import BatchInfo, Eyes, MatchLevel, logger  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from `applitools.core` or "
    "`applitools.selenium` instead"
)
