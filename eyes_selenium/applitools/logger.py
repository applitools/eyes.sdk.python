from .core import logger  # noqa
from .core.logger import *  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from  `applitools.core` instead"
)
