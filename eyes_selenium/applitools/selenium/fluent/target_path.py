from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    pass


class Locator(object):
    def __init__(self, parent, selector_or_by, selector=None):
        self.parent = parent
        if selector is None:
            self.by = By.CSS_SELECTOR if selector_or_by else None
            self.selector = selector_or_by
        else:
            self.by = selector_or_by
            self.selector = selector

    def __eq__(self, other):
        return type(self) is type(other) and vars(self) == vars(other)

    def __repr__(self):
        parent = repr(self.parent) if self.parent else "TargetPath"
        if self.by == By.CSS_SELECTOR:
            return parent + ".{}({!r})".format(
                self.FACTORY_METHOD, self.selector  # noqa
            )
        else:
            return parent + ".{}({}, {!r})".format(
                self.FACTORY_METHOD, _by_repr(self.by), self.selector  # noqa
            )


class TargetPath(object):
    @staticmethod
    def region(selector_or_by, selector=None):
        return RegionLocator(None, selector_or_by, selector)

    @staticmethod
    def frame(number_or_id_or_name_or_by, selector=None):
        return FrameLocator(None, number_or_id_or_name_or_by, selector)

    @staticmethod
    def shadow(selector_or_by, selector=None):
        return ShadowDomLocator(None, selector_or_by, selector)


class ShadowDomLocator(Locator):
    FACTORY_METHOD = "shadow"

    def region(self, selector_or_by, selector=None):
        return RegionLocator(self, selector_or_by, selector)

    def frame(self, number_or_id_or_name_or_by, selector=None):
        return FrameLocator(self, number_or_id_or_name_or_by, selector)

    def shadow(self, selector_or_by, selector=None):
        return ShadowDomLocator(self, selector_or_by, selector)


class RegionLocator(Locator):
    FACTORY_METHOD = "region"


class FrameLocator(Locator):
    FACTORY_METHOD = "frame"

    def __init__(self, parent, number_or_id_or_name_or_by, selector=None):
        if selector is None:
            super(FrameLocator, self).__init__(parent, None, None)
            self.number_or_id_or_name = number_or_id_or_name_or_by
        else:
            super(FrameLocator, self).__init__(
                parent, number_or_id_or_name_or_by, selector
            )
            self.number_or_id_or_name = None

    def __repr__(self):
        parent = repr(self.parent) if self.parent else "TargetPath"
        if self.number_or_id_or_name is not None:
            return parent + ".{}({!r})".format(
                self.FACTORY_METHOD, self.number_or_id_or_name
            )
        else:
            return parent + ".{}({}, {!r})".format(
                self.FACTORY_METHOD, _by_repr(self.by), self.selector
            )

    def region(self, selector_or_by, selector=None):
        return RegionLocator(self, selector_or_by, selector)

    def frame(self, number_or_id_or_name_or_by, selector=None):
        return FrameLocator(self, number_or_id_or_name_or_by, selector)

    def shadow(self, selector_or_by, selector=None):
        return ShadowDomLocator(self, selector_or_by, selector)


def _by_repr(by):
    return "By." + by.upper().replace(" ", "_")
