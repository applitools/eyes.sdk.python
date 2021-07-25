from typing import TYPE_CHECKING, List, Union

from applitools.common.utils.custom_types import AnyWebElement, CssSelector

if TYPE_CHECKING:
    Locator = Union[CssSelector, AnyWebElement, List[CssSelector]]  # typedef
