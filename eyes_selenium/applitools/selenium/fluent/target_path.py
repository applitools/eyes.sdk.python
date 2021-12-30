from copy import deepcopy
from typing import TYPE_CHECKING, overload

from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    from typing import Text


class TargetPath(object):
    @overload
    def __init__(self, css_selector):
        # type: (Text) -> None
        pass

    @overload
    def __init__(self, by, selector):
        # type: (Text, Text) -> None
        pass

    def __init__(self, css_selector_or_by, selector=None, shadow_path=None):
        if selector is not None:
            self.by = css_selector_or_by
            self.selector = selector
        else:
            self.by = By.CSS_SELECTOR
            self.selector = css_selector_or_by
        self.shadow_path = shadow_path

    @overload
    def shadow(self, css_selector):
        # type: (Text) -> TargetPath
        pass

    @overload
    def shadow(self, by, selector):
        # type: (Text, Text) -> TargetPath
        pass

    def shadow(self, css_selector_or_by, selector=None):
        copy = deepcopy(self)
        path = copy
        while path.shadow_path is not None:
            path = path.shadow_path
        path.shadow_path = TargetPath(css_selector_or_by, selector)
        return copy

    def __eq__(self, that):
        # type: (TargetPath) -> bool
        return type(self) is type(that) and vars(self) == vars(that)

    def __repr__(self):
        # type: () -> Text
        parts = []
        call, path = type(self).__name__, self
        while path is not None:
            if path.by == By.CSS_SELECTOR:
                parts.append("{}({!r})".format(call, path.selector))
            else:
                by = "By." + path.by.upper().replace(" ", "_")
                parts.append("{}({}, {!r})".format(call, by, path.selector))
            call, path = ".shadow", path.shadow_path
        return "".join(parts)
