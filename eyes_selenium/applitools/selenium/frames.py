import copy
import typing as tp

from applitools.common import EyesError, Point

if tp.TYPE_CHECKING:
    from applitools.common.utils.custom_types import FrameReference, RectangleSize

__all__ = ("Frame", "FrameChain")


class Frame(object):
    """
    Encapsulates a frame/iframe. This is a generic type class,
    and it's actual type is determined by the reference used by the user in
    order to switch into the frame.
    """

    __slots__ = (
        "reference",
        "location",
        "outer_size",
        "inner_size",
        "parent_scroll_position",
        "_scroll_root_element",
        "_original_overflow",
    )

    def __init__(
        self, reference, location, outer_size, inner_size, parent_scroll_position
    ):
        # type: (FrameReference, Point, RectangleSize, RectangleSize, Point) -> None
        """
        :param reference: The web element for the frame, used as a reference to
                          switch  into the frame.
        :param location: The location of the frame within the current frame.
        :param outer_size: The frame element outerSize (i.e., the outer_size of the
                           frame on the screen, not the internal document outer_size).
        :param inner_size: The frame element inner outerSize (i.e., the outer_size
                           of the frame actual outer_size, without borders).
        :param parent_scroll_position: The scroll location of the frame.
        """
        self._scroll_root_element = None
        self._original_overflow = None

        self.reference = reference
        self.location = location
        self.outer_size = outer_size
        self.inner_size = inner_size
        self.parent_scroll_position = parent_scroll_position

    def __str__(self):
        return "Frame: {}".format(self.reference)


class FrameChain(tp.Sequence[Frame]):
    __slots__ = ("_frames",)

    def __init__(self, frame_chain=None):
        self._frames = []
        if frame_chain is not None:
            assert isinstance(frame_chain, FrameChain), "Must be a FrameChain"
            self._frames = copy.copy(frame_chain._frames)

    def __iter__(self):
        return iter(self._frames)

    def __getitem__(self, item):
        return self._frames[item]

    def __len__(self):
        return len(self._frames)

    def __str__(self):
        return "FrameChain with {} frames".format(len(self))

    def __eq__(self, other):
        cl1, cl2 = len(self._frames), len(other)
        if cl1 != cl2:
            return False
        for i in range(cl1):
            if self._frames[i].id_ != other[i].id_:
                return False
        return True

    def clear(self):
        self._frames = []

    @property
    def size(self):
        return len(self)

    @property
    def peek(self):
        # type: () -> Frame
        return self[-1]

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
        location = Point.create_top_left()
        for frame in self:
            location.offset_by_location(frame.location)
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
