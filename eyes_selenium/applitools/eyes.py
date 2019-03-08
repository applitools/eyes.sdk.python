from .selenium import (  # noqa
    BatchInfo,
    ExactMatchSettings,
    Eyes,
    FailureReports,
    MatchLevel,
    logger,
)

logger.deprecation(
    "Will be deprecated in version 4.0. Import from `applitools.core` or "
    "`applitools.selenium` instead"
)
