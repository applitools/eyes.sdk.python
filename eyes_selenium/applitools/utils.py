from .core import logger  # noqa
from .core.utils import general_utils, image_utils  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from  `applitools.core` instead"
)
