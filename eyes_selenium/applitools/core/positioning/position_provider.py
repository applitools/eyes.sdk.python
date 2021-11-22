import abc
import typing

from applitools.common.geometry import Point
from applitools.common.utils import ABC, iteritems

if typing.TYPE_CHECKING:
    from typing import Any, List, Optional

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


class PositionProvider(ABC):
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

    def get_state(self):
        # type: () -> PositionMemento
        """Get the current state of the position provider.

        This is different from :eyes_selenium_utils:`get_current_position()` in that the
        state of the position provider
        might include other model than just the coordinates. For example a CSS
        translation based position provider (in WebDriver based SDKs), might
        save the entire "transform" style value as its state.

        Returns:
            The current state of the position provider, which can later be
            restored by  passing it as a parameter to :self:`restore_state`.
        """
        return PositionMemento(self.get_current_position())

    def restore_state(self, state):
        # type: (PositionMemento) -> None
        """Restores the state of the position provider to the state provided as a
        parameter.

        Args:
            state: The state to restore to.
        """
        self.set_position(state.position)


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
