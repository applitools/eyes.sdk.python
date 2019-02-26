from .core import logger  # noqa
from .selenium import StitchMode  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from `applitools.selenium` instead"
)
