import copy
import typing as tp

import attr

from applitools.common import EyesError, Point, RectangleSize, logger

from . import eyes_selenium_utils

if tp.TYPE_CHECKING:
    from typing import Optional

    from applitools.common.utils.custom_types import AnyWebDriver

    from .webelement import EyesWebElement

__all__ = ("Frame", "FrameChain")


@attr.s(slots=True)
class Frame(object):
    """
    Encapsulates a frame/iframe. This is a generic type class,
    and it's actual type is determined by the reference used by the user in
    order to switch into the frame.
    :param reference: The web element for the frame, used as a reference to
                      switch  into the frame.
    :param location: The location of the frame within the current frame.
    :param outer_size: The frame element outerSize (i.e., the outer_size of the
                       frame on the screen, not the internal document outer_size).
    :param inner_size: The frame element inner outerSize (i.e., the outer_size
                       of the frame actual outer_size, without borders).
    :param parent_scroll_position: The scroll location of the frame.
    :param scroll_root_element: The element used for content scrolling within frame.
    """

    reference = attr.ib()  # type: EyesWebElement
    location = attr.ib()  # type: Point
    outer_size = attr.ib()  # type: RectangleSize
    inner_size = attr.ib()  # type: RectangleSize
    parent_scroll_position = attr.ib()
    scroll_root_element = attr.ib()  # type: EyesWebElement
    original_overflow = attr.ib(default=None)

    def return_to_original_overflow(self, driver):
        # type: (AnyWebDriver) -> None
        root_element = eyes_selenium_utils.get_underlying_webelement(
            self._scroll_root_element(driver)
        )
        logger.debug(
            "returning overflow of element to its original value: {}".format(
                root_element
            )
        )
        driver.execute_script(
            "arguments[0].style.overflow='%s'" % self.original_overflow, root_element
        )

    def _scroll_root_element(self, driver):
        scroll_root = self.scroll_root_element
        if scroll_root is None or not scroll_root.is_attached_to_page:
            logger.debug("no scroll root element. selecting default.")
            scroll_root = driver.find_element_by_tag_name("html")
        return scroll_root

    def hide_scrollbars(self, driver):
        scroll_root_element = eyes_selenium_utils.get_underlying_webelement(
            self._scroll_root_element(driver)
        )
        self.original_overflow = driver.execute_script(
            "var origOF = arguments[0].style.overflow; arguments["
            "0].style.overflow='hidden'; return origOF;",
            scroll_root_element,
        )
        return self.original_overflow


@attr.s(slots=True, init=False, eq=False)
class FrameChain(tp.Sequence[Frame]):
    _frames = attr.ib()

    def __init__(self, frame_chain=None):
        # type: (Optional[FrameChain]) -> None
        self._frames = []
        if frame_chain is not None:
            assert isinstance(frame_chain, FrameChain), "Must be a FrameChain"
            self._frames = copy.copy(frame_chain._frames)

    def __iter__(self):
        return iter(self._frames)

    def __getitem__(self, item):
        return self._frames[item]

    def __delitem__(self, item):
        del self._frames[item]

    def __len__(self):
        # type: () -> int
        return len(self._frames)

    def __str__(self):
        return "FrameChain with {} frames".format(len(self))

    def __eq__(self, other):
        cl1, cl2 = len(self._frames), len(other)
        if cl1 != cl2:
            return False
        return all(self._frames[i].id_ == other[i].id_ for i in range(cl1))

    def clear(self):
        # type: () -> None
        del self._frames[:]

    @property
    def size(self):
        # type: () -> int
        return len(self)

    @property
    def peek(self):
        # type: () -> Optional[Frame]
        if self._frames:
            return self[-1]
        return None

    def push(self, frame):
        # type: (Frame) -> None
        assert isinstance(frame, Frame), "frame must be instance of Frame!"
        self._frames.append(frame)

    def pop(self):
        # type: () -> Frame
        return self._frames.pop()

    @property
    def current_frame_offset(self):
        # type: () -> Point
        location = Point.ZERO()
        for frame in self:
            location = location.offset(frame.location)
        return location

    @property
    def current_frame_size(self):
        # type: () -> RectangleSize
        return self.peek.inner_size

    @property
    def current_frame_inner_size(self):
        # type: () -> RectangleSize
        return self.peek.outer_size

    @property
    def default_content_scroll_position(self):
        # type: () -> tp.Union[Point, EyesError]
        if len(self) == 0:
            raise EyesError("No frames in frame chain")
        result = self[0].parent_scroll_position
        return Point(result.x, result.y)

    def clone(self):
        # type: () -> FrameChain
        return FrameChain(self)
