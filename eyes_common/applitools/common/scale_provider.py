from .utils.compat import ABC


class ScaleProvider(ABC):
    UNKNOWN_SCALE_RATIO = 0.0

    def __init__(self, *args, **kwargs):
        self._scale_ratio = self.UNKNOWN_SCALE_RATIO
        self.device_pixel_ratio = 1

    @property
    def scale_ratio(self):
        return self._scale_ratio

    def update_scale_ratio(self, image_to_scale_width):
        pass
