from applitools.common.configuration import BatchInfo
from applitools.common.metadata import FailureReports
from applitools.сommon import logger  # noqa

from .selenium import (  # noqa
    BatchInfo,
    ExactMatchSettings,
    Eyes,
    FailureReports,
    MatchLevel,
)

logger.deprecation(
    "Will be deprecated in version 4.0. Import from `applitools.core` or "
    "`applitools.selenium` instead"
)
