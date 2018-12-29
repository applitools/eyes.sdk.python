from __future__ import absolute_import

import typing as tp

import attr
from PIL import Image
from multimethod import multidispatch

from applitools.core import RegionProvider
from applitools.core.utils import image_utils
from applitools.core.errors import EyesError
from applitools.core.geometry import Region

__all__ = ('FloatingBounds', 'FloatingRegion', 'Target')


# TODO: Refactor this


class _NopRegionWrapper(RegionProvider):
    pass


# Floating regions related classes.
class FloatingBounds(object):
    def __init__(self, max_left_offset=0, max_up_offset=0, max_right_offset=0, max_down_offset=0):
        # type: (int, int, int, int) -> None
        self.max_left_offset = max_left_offset
        self.max_up_offset = max_up_offset
        self.max_right_offset = max_right_offset
        self.max_down_offset = max_down_offset


@attr.s
class FloatingRegion(RegionProvider):
    _region = attr.ib()  # The inner region (the floating part).
    _bounds = attr.ib()  # The outer rectangle bounding the inner region.

    def __getstate__(self):
        return dict(top=self.region.top,
                    left=self.region.left,
                    width=self.region.width,
                    height=self.region.height,
                    maxLeftOffset=self.bounds.max_left_offset,
                    maxUpOffset=self.bounds.max_up_offset,
                    maxRightOffset=self.bounds.max_right_offset,
                    maxDownOffset=self.bounds.max_down_offset)

    # This is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError('Cannot create FloatingRegion instance from dict!')

    def _str_(self):
        return "{0} {{region: {1}, bounds: {2}}}".format(self.__class__.__name__, self.region, self.bounds)


# Main class for the module
class Target(object):
    """
    Target for an eyes.check_window/region.
    """

    def __init__(self):
        # type: () -> None
        self._ignore_caret = True
        self._ignore_regions = []  # type: tp.List
        self._floating_regions = []  # type: tp.List
        self._image = None
        self._target_region = None
        self._timeout = None

    def ignore(self, *regions):
        # type: (*tp.Union['Region']) -> Target
        """
        Add ignore regions to this target.
        :param regions: Ignore regions to add. Can be of several types:
            (Region) Region specified by coordinates
            (IgnoreRegionBySelector) Region specified by a selector of an element
            (IgnoreRegionByElement) Region specified by a WebElement instance.
        :return: (Target) self.
        """
        for region in regions:
            if region is None:
                continue
            if isinstance(region, Region):
                self._ignore_regions.append(_NopRegionWrapper(region))
            else:
                self._ignore_regions.append(region)
        return self

    def floating(self, *regions):
        # type: (*tp.Union['FloatingRegion']) -> Target
        """
        Add floating regions to this target.
        :param regions: Floating regions to add. Can be of several types:
            (Region) Region specified by coordinates
            (FloatingRegionByElement) Region specified by a WebElement instance.
            (FloatingRegionBySelector) Region specified by a selector of an element
        :return: (Target) self.
        """
        for region in regions:
            if region is None:
                continue
            self._floating_regions.append(region)
        return self

    def ignore_caret(self, ignore=True):
        # type: (bool) -> Target
        """
        Whether we should ignore caret when matching screenshots.
        """
        self._ignore_caret = ignore
        return self

    def get_ignore_caret(self):
        return self._ignore_caret

    @property
    def ignore_regions(self):
        # type: () -> tp.List
        """The ignore regions defined on the current target."""
        return self._ignore_regions

    @property
    def floating_regions(self):
        # type: () -> tp.List
        """The floating regions defined on the current target."""
        return self._floating_regions

    def timeout(self, timeout):
        self._timeout = timeout
        return self

    def image(self, image_or_path):
        # type: (tp.Union[Image.Image, tp.Text]) -> Target
        self._image = image_dispatch(image_or_path)
        return self

    def region(self, image_or_path, rect):
        # type: (tp.Union[Image.Image, tp.Text], Region) -> Target
        target = self.image(image_or_path)
        target._target_region = rect
        return target


@multidispatch
def image_dispatch(image):
    raise TypeError('Not supported type.')


@image_dispatch.register(Image.Image)  # type: ignore
def _image_dispatch(image):
    return image


@image_dispatch.register(tp.Text)  # type: ignore
@image_dispatch.register(str)
def _image_dispatch(image_path):
    image = image_utils.image_from_file(image_path)
    return image
