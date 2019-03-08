from .app_output import *  # noqa
from .capture import *  # noqa
from .configuration import *  # noqa
from .errors import *  # noqa
from .geometry import *  # noqa
from .logger import *  # noqa
from .match import *  # noqa
from .match_window_data import *  # noqa
from .metadata import *  # noqa
from .test_results import *  # noqa


class StitchMode(object):
    """For backward compatibility for eyes.selenium"""

    Scroll = "Scroll"
    CSS = "CSS"


__all__ = (
    logger.__all__  # noqa
    + configuration.__all__  # noqa
    + errors.__all__  # noqa
    + geometry.__all__  # noqa
    + match.__all__  # noqa
    + metadata.__all__  # noqa
    + app_output.__all__  # noqa
    + capture.__all__  # noqa
    + match_window_data.__all__  # noqa
    + test_results.__all__  # noqa
    + ("logger", "StitchMode")  # noqa
)
