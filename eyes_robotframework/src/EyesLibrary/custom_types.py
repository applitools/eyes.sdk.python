from __future__ import absolute_import, unicode_literals

from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    # TODO improve typing here
    from applitools.common.utils.custom_types import CssSelector

    Locator = Union[CssSelector, List[CssSelector]]  # typedef
