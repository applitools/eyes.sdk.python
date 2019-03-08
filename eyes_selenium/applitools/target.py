from .common import logger  # noqa
from .selenium.fluent.target import *  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from  `applitools.selenium` instead"
)
