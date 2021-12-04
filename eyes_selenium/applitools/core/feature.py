from enum import Enum

from applitools.common import deprecated

deprecated.module(__name__, "feature flags are not supported anymore")


class Feature(Enum):
    TARGET_WINDOW_CAPTURES_SELECTED_FRAME = "Target window captures selected frame"
    SCALE_MOBILE_APP = "Scale mobile app"
