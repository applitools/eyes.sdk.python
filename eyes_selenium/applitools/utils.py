from .common import logger  # noqa
from .common.utils import general_utils, image_utils  # noqa

logger.deprecation(
    "Will be deprecated in version 4.0. Import from  `applitools.core` instead"
)
