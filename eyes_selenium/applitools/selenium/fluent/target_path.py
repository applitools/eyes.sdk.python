from typing import TYPE_CHECKING, overload

import attr
from selenium.webdriver.common.by import By
from six import string_types

if TYPE_CHECKING:
    from typing import Text

    from applitools.common.utils.custom_types import BySelector


@attr.s(repr=False)
class ElementPath(object):
    by = attr.ib(
        type=string_types, repr=lambda v: "By.{}".format(v.upper().replace(" ", "_"))
    )
    selector = attr.ib(type=string_types)
    shadow_path = attr.ib(type="ElementPath", default=None)

    @overload
    def shadow(self, css_selector):
        # type: (Text) -> ElementPath
        pass

    @overload
    def shadow(self, by_selector):
        # type: (BySelector) -> ElementPath
        pass

    @overload
    def shadow(self, elemement_path):
        # type: (ElementPath) -> ElementPath
        pass

    def shadow(self, selector):
        if self.shadow_path:
            self.shadow_path.shadow(selector)
        elif isinstance(selector, string_types):
            self.shadow_path = ElementPath(By.CSS_SELECTOR, selector)
        elif isinstance(selector, list) and len(selector) == 2:
            self.shadow_path = ElementPath(*selector)
        elif isinstance(selector, ElementPath):
            self.shadow_path = selector
        else:
            raise TypeError(
                "Unsupported selector {} of type {}".format(selector, type(selector))
            )
        return self

    def __repr__(self):
        by = "By.{}".format(self.by.upper().replace(" ", "_"))
        shadow = ", " + repr(self.shadow_path) if self.shadow_path else ""
        return "ElementPath({}, {!r}{})".format(by, self.selector, shadow)


class TargetPath(object):
    @staticmethod
    def id(id_):
        # type: (Text) -> ElementPath
        return ElementPath(By.ID, id_)

    @staticmethod
    def xpath(xpath):
        # type: (Text) -> ElementPath
        return ElementPath(By.XPATH, xpath)

    @staticmethod
    def link_text(link_text):
        # type: (Text) -> ElementPath
        return ElementPath(By.LINK_TEXT, link_text)

    @staticmethod
    def partial_link_text(partial_link_text):
        # type: (Text) -> ElementPath
        return ElementPath(By.PARTIAL_LINK_TEXT, partial_link_text)

    @staticmethod
    def name(name):
        # type: (Text) -> ElementPath
        return ElementPath(By.NAME, name)

    @staticmethod
    def tag_name(tag_name):
        # type: (Text) -> ElementPath
        return ElementPath(By.TAG_NAME, tag_name)

    @staticmethod
    def class_name(class_name):
        # type: (Text) -> ElementPath
        return ElementPath(By.CLASS_NAME, class_name)

    @staticmethod
    def css_selector(css_selector):
        # type: (Text) -> ElementPath
        return ElementPath(By.CSS_SELECTOR, css_selector)
