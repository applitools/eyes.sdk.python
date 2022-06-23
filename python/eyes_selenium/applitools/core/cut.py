import math
from abc import ABCMeta, abstractmethod

import attr

__all__ = ("FixedCutProvider", "UnscaledFixedCutProvider", "NullCutProvider")

from six import add_metaclass


@add_metaclass(ABCMeta)
@attr.s
class CutProvider(object):
    header = attr.ib()  # type: int
    footer = attr.ib()  # type: int
    left = attr.ib()  # type: int
    right = attr.ib()  # type: int

    @abstractmethod
    def scale(self, scale_ratio):
        # type: (float) -> CutProvider
        """Get a scaled version of the cut provider"""


class FixedCutProvider(CutProvider):
    def scale(self, scale_ratio):
        # type: (float) -> FixedCutProvider
        cut_provider = FixedCutProvider(
            math.ceil(self.header * scale_ratio),
            math.ceil(self.footer * scale_ratio),
            math.ceil(self.left * scale_ratio),
            math.ceil(self.right * scale_ratio),
        )
        return cut_provider


class UnscaledFixedCutProvider(CutProvider):
    def scale(self, scale_ratio):
        # type: (float) -> UnscaledFixedCutProvider
        if isinstance(self, NullCutProvider):
            return self

        cut_provider = UnscaledFixedCutProvider(
            self.header, self.footer, self.left, self.right
        )
        return cut_provider


class NullCutProvider(UnscaledFixedCutProvider):
    def __init__(self):
        super(NullCutProvider, self).__init__(0, 0, 0, 0)
