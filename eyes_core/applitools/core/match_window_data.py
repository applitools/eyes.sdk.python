from typing import Text

import attr

from applitools.common import EyesScreenshot
from applitools.common.match_window_data import MatchWindowData
from applitools.common.metadata import SessionStartInfo

__all__ = ("MatchWindowDataWithScreenshot", "MatchSingleWindowData")


@attr.s
class MatchWindowDataWithScreenshot(object):
    """
    A container for a MatchWindowData along with the screenshot used for creating
    it. (We specifically avoid inheritance so we don't have to deal with serialization issues).
    """

    match_window_data = attr.ib()  # type: MatchWindowData
    screenshot = attr.ib()  # type: EyesScreenshot


@attr.s
class MatchSingleWindowData(MatchWindowData):
    start_info = attr.ib(type=SessionStartInfo)  # type: SessionStartInfo
    update_baseline = attr.ib()  # type: bool
    update_baseline_if_different = attr.ib()  # type: bool
    update_baseline_if_new = attr.ib()  # type: bool
    remove_session = attr.ib()  # type: bool
    remove_session_if_matching = attr.ib()  # type: bool
    agent_id = attr.ib()  # type: Text
