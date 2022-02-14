from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from six import string_types

if TYPE_CHECKING:
    from typing import Optional, Text, Union

    from selenium.webdriver.remote.webelement import WebElement


class PathNodeValue(object):
    def __eq__(self, other):
        # type: (PathNodeValue) -> bool
        return type(self) is type(other) and vars(self) == vars(other)


class ElementReference(PathNodeValue):
    def __init__(self, element):
        # type: (WebElement) -> None
        self.element = element

    def repr_args(self, _):
        return "{!r}".format(self.element)


class ElementSelector(PathNodeValue):
    def __init__(self, selector_or_by, selector=None):
        # type: (Text, Optional[Text]) -> None
        if selector is None:
            self.by = By.CSS_SELECTOR
            self.selector = selector_or_by
        else:
            self.by = selector_or_by
            self.selector = selector

    def repr_args(self, frame_call_args):
        if self.by == By.CSS_SELECTOR and not frame_call_args:
            return "{!r}".format(self.selector)
        else:
            by = "By." + self.by.upper().replace(" ", "_")
            return "{}, {!r}".format(by, self.selector)


class FrameSelector(PathNodeValue):
    def __init__(self, number_or_id_or_name):
        # type: (Union[int, Text]) -> None
        self.number_or_id_or_name = number_or_id_or_name

    def repr_args(self, _):
        return "{!r}".format(self.number_or_id_or_name)


class Locator(object):
    def __init__(self, parent, value):
        # type: (Optional[Locator], PathNodeValue) -> None
        self.parent = parent
        self.value = value

    def __eq__(self, other):
        return type(self) is type(other) and vars(self) == vars(other)

    def __repr__(self):
        return self._repr(False)

    def _repr(self, frame_call_args):
        parent = repr(self.parent) if self.parent else "TargetPath"
        args = self.value.repr_args(frame_call_args)
        return parent + ".{}({})".format(self.FACTORY_METHOD, args)


class TargetPath(object):
    @staticmethod
    def region(element_or_selector_or_by, selector=None):
        return _region(None, element_or_selector_or_by, selector)

    @staticmethod
    def frame(element_or_number_or_id_or_name_or_by, selector=None):
        return _frame(None, element_or_number_or_id_or_name_or_by, selector)

    @staticmethod
    def shadow(element_or_selector_or_by, selector=None):
        return _shadow(None, element_or_selector_or_by, selector)


class ShadowDomLocator(Locator):
    FACTORY_METHOD = "shadow"

    def region(self, element_or_selector_or_by, selector=None):
        return _region(self, element_or_selector_or_by, selector)

    def frame(self, element_or_number_or_id_or_name_or_by, selector=None):
        return _frame(self, element_or_number_or_id_or_name_or_by, selector)

    def shadow(self, element_or_selector_or_by, selector=None):
        return _shadow(self, element_or_selector_or_by, selector)


class RegionLocator(Locator):
    FACTORY_METHOD = "region"


class FrameLocator(Locator):
    FACTORY_METHOD = "frame"

    def region(self, element_or_selector_or_by, selector=None):
        return _region(self, element_or_selector_or_by, selector)

    def frame(self, element_or_number_or_id_or_name_or_by, selector=None):
        return _frame(self, element_or_number_or_id_or_name_or_by, selector)

    def shadow(self, element_or_selector_or_by, selector=None):
        return _shadow(self, element_or_selector_or_by, selector)

    def __repr__(self):
        return self._repr(True)


def _frame(parent, element_or_number_or_id_or_name_or_by, selector=None):
    if selector is not None:
        by = element_or_number_or_id_or_name_or_by
        return FrameLocator(parent, ElementSelector(by, selector))
    elif isinstance(element_or_number_or_id_or_name_or_by, (int, string_types)):
        number_or_id_or_name = element_or_number_or_id_or_name_or_by
        return FrameLocator(parent, FrameSelector(number_or_id_or_name))
    else:
        element = element_or_number_or_id_or_name_or_by
        return FrameLocator(parent, ElementReference(element))


def _shadow(parent, element_or_selector_or_by, selector=None):
    if selector is not None:
        by = element_or_selector_or_by
        return ShadowDomLocator(parent, ElementSelector(by, selector))
    elif isinstance(element_or_selector_or_by, string_types):
        selector = element_or_selector_or_by
        return ShadowDomLocator(parent, ElementSelector(By.CSS_SELECTOR, selector))
    else:
        element = element_or_selector_or_by
        return ShadowDomLocator(parent, ElementReference(element))


def _region(parent, element_or_selector_or_by, selector=None):
    if selector is not None:
        by = element_or_selector_or_by
        return RegionLocator(parent, ElementSelector(by, selector))
    elif isinstance(element_or_selector_or_by, string_types):
        selector = element_or_selector_or_by
        return RegionLocator(parent, ElementSelector(By.CSS_SELECTOR, selector))
    else:
        element = element_or_selector_or_by
        return RegionLocator(parent, ElementReference(element))
