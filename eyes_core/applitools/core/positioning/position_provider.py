import abc
import typing

import attr

from applitools.common.geometry import Point
from applitools.common.utils import ABC

if typing.TYPE_CHECKING:
    from typing import List, Optional
    from applitools.common import RectangleSize

__all__ = ("PositionProvider", "InvalidPositionProvider")


@attr.s
class PositionProvider(ABC):
    _states = attr.ib(init=False, factory=list)

    @abc.abstractmethod
    def get_current_position(self):
        # type: () -> Optional[Point]
        """
        :return: The current position, or `None` if position is not available.
        """

    @abc.abstractmethod
    def set_position(self, location):
        # type: (Point) -> Point
        """
        Go to the specified location.

        :param location: The position to set
        """

    @abc.abstractmethod
    def get_entire_size(self):
        # type: () -> RectangleSize
        """
        :return: The entire size of the container which the position is relative to.
        """

    def push_state(self):
        """
        Adds the current position to the states list.
        """
        self._states.append(self.get_current_position())

    def pop_state(self):
        """
        Sets the position to be the last position added to the states list.
        """
        self.set_position(self._states.pop())

    @property
    def states(self):
        # type: () -> List[Point]
        if self._states:
            return self._states[-1]


class InvalidPositionProvider(PositionProvider):
    """
    An implementation of :py:class:`PositionProvider` which throws an exception
    for every method. Can be used as a placeholder until an actual
    implementation is set.
    """

    def get_current_position(self):
        raise NotImplementedError("This class does not implement methods!")

    def set_position(self, location):
        # type: (Point) -> None
        raise NotImplementedError("This class does not implement methods!")

    def get_entire_size(self):
        raise NotImplementedError("This class does not implement methods!")
