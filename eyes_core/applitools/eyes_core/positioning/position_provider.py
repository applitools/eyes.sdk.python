import abc
import typing as tp

import attr

from applitools.eyes_core import Point
from applitools.eyes_core.utils.compat import ABC

if tp.TYPE_CHECKING:
    from applitools.eyes_core.utils.custom_types import ViewPort

__all__ = ('PositionProvider', 'InvalidPositionProvider', 'PositionMemento')


@attr.s
class PositionProvider(ABC):
    _states = attr.ib(init=False, factory=list)

    @abc.abstractmethod
    def get_current_position(self):
        # type: () -> tp.Optional[Point]
        """
        :return: The current position, or `None` if position is not available.
        """

    @abc.abstractmethod
    def set_position(self, location):
        # type: (Point) -> None
        """
        Go to the specified location.

        :param location: The position to set
        """

    @property
    @abc.abstractmethod
    def get_entire_size(self):
        # type: () -> ViewPort
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


class InvalidPositionProvider(PositionProvider):
    """
    An implementation of :py:class:`PositionProvider` which throws an exception
    for every method. Can be used as a placeholder until an actual
    implementation is set.
    """

    def get_current_position(self):
        raise NotImplementedError("This class does not implement methods!")

    def set_position(self, location: Point):
        raise NotImplementedError("This class does not implement methods!")

    def get_entire_size(self):
        raise NotImplementedError("This class does not implement methods!")


class PositionMemento(ABC):
    """
    A base class for position related memento instances. This is intentionally
    not an interface, since the mementos might vary in their interfaces.
    """
