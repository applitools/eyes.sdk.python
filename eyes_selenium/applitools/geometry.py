from .core import logger  # noqa
from .core.geometry import *  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from  "
    "`applitools.core` or `applitools.selenium` instead"
)
