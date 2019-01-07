from __future__ import absolute_import

import typing as tp

from PIL import Image
from multimethod import multidispatch

from applitools.core import RegionProvider
from applitools.core.utils import image_utils
from applitools.core.errors import EyesError
from applitools.core.geometry import Region

if tp.TYPE_CHECKING:
    from applitools.images.capture import EyesImagesScreenshot

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


class FloatingRegion(RegionProvider):
    def __init__(self, region, bounds):
        # type: (Region, FloatingBounds) -> None
        """
        :param region: The inner region (the floating part).
        :param bounds: The outer rectangle bounding the inner region.
        """
        self.region = region  # type: Region
        self.bounds = bounds  # type: FloatingBounds

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

    __ignore_regions = None  # type: tp.Optional[tp.List]
    __floating_regions = None  # type: tp.Optional[tp.List]
    _image = None  # type: tp.Optional[EyesImagesScreenshot]
    _target_region = None  # type: tp.Optional[Region]
    _timeout = -1

    ignore_caret = None

    def ignore(self, *regions):
        # type: (*tp.Union[Region]) -> Target
        """
        Add ignore regions to this target.
        :param regions: Region specified by coordinates
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
        # type: (*tp.Union[FloatingRegion]) -> Target
        """
        Add floating regions to this target.
        :param regions: Floating regions to add. Can be of several types:
            (Region) Region specified by coordinates
            (FloatingRegion) Region specified by Region and FloatingBounds instance.
        :return: (Target) self.
        """
        for region in regions:
            if region is None:
                continue
            self._floating_regions.append(region)
        return self

    @property
    def _floating_regions(self):
        if self.__floating_regions is None:
            self.__floating_regions = []
        return self.__floating_regions

    @property
    def _ignore_regions(self):
        if self.__ignore_regions is None:
            self.__ignore_regions = []
        return self.__ignore_regions

    def timeout(self, timeout):
        self._timeout = timeout
        return self

    def image(self, image_or_path):
        # type: (tp.Union[Image.Image, tp.Text]) -> Target
        self._image = _image_dispatch(image_or_path)
        return self

    def region(self, image_or_path, rect):
        # type: (tp.Union[Image.Image, tp.Text], Region) -> Target
        target = self.image(image_or_path)
        target._target_region = rect
        return target


@multidispatch
def _image_dispatch(image):
    raise TypeError('Not supported type.')


@_image_dispatch.register(Image.Image)  # type: ignore
def __image_dispatch(image):
    return image


@_image_dispatch.register(tp.Text)  # type: ignore
@_image_dispatch.register(str)
def __image_dispatch(image_path):
    image = image_utils.image_from_file(image_path)
    return image
