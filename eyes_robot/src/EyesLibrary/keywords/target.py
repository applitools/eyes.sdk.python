from typing import TYPE_CHECKING, List, Optional, Text, Tuple, Union

from applitools.common import MatchResult, Region

from ..base import LibraryComponent, keyword

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement, FrameReference


class CheckKeywords(LibraryComponent):
    @keyword("Eyes Check")
    def check(self, target):
        # TODO: add target builder from keywords
        self.current_eyes.check(target)

    @keyword("Eyes Check Window")
    def check_window(self, tag=None, fully=None, match_timeout=-1):
        # type: (Optional[Text], Optional[bool], int) -> MatchResult
        return self.current_eyes.check_window(tag, match_timeout, fully)

    @keyword("Eyes Check Region")
    def check_region(
        self,
        region,  # type: Union[Region,Text,List,Tuple,AnyWebElement]
        tag=None,  # type: Optional[Text]
        fully=False,  # type: bool
        match_timeout=-1,  # type: int
    ):
        # type: (...) -> MatchResult
        return self.current_eyes.check_region(region, tag, match_timeout, fully)

    @keyword("Eyes Check Frame")
    def check_frame(self, frame_reference, tag=None, match_timeout=-1):
        # type: (FrameReference, Optional[Text], int) -> MatchResult
        return self.current_eyes.check_frame(frame_reference, tag, match_timeout)


class TargetKeywords(LibraryComponent):
    @keyword("Eyes Target Window")
    def window(self):
        ...

    @keyword("Eyes Target Region")
    def region(self):
        ...

    @keyword("Eyes Target Frame")
    def frame(self):
        ...
