import abc
import typing

import attr

from applitools.common.geometry import Point
from applitools.common.utils import ABC, iteritems

if typing.TYPE_CHECKING:
    from typing import List, Optional, Any
    from applitools.common import RectangleSize


class PositionMemento(object):
    """
    A base class for position related memento instances. This is intentionally
    not an interface, since the mementos might vary in their interfaces.
    """

    def __init__(self, position, **kwargs):
        # type: (Point, **Any) -> None
        self.position = position
        for name, val in iteritems(kwargs):
            setattr(self, name, val)

    def __str__(self):
        return "PositionMemento(position={}, ...)".format(self.position)


@attr.s
class PositionProvider(ABC):
    _states = attr.ib(init=False, factory=list)  # type: List[PositionMemento]
    _last_set_position = attr.ib(init=False, default=None)  # type: Point
    _state_index = -1

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
        self._states.append(PositionMemento(self.get_current_position()))
        self._state_index += 1

    def pop_state(self):
        """
        Sets the position to be the last position added to the states list.
        """
        state = self._states.pop()
        self._state_index -= 1
        self.set_position(state.position)
        self._last_set_position = state.position

    @property
    def states(self):
        # type: () -> List[PositionMemento]
        return self._states

    @property
    def current_state(self):
        # type: () -> PositionMemento
        if self._state_index >= 0:
            return self._states[self._state_index]
        return PositionMemento(self.get_current_position())

    def __enter__(self):
        self.push_state()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop_state()
        return self


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
