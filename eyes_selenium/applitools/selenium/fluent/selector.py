import typing
import uuid
from typing import Text

import attr

from applitools.core.fluent import GetSelector

if typing.TYPE_CHECKING:
    from applitools.selenium import Eyes, eyes_selenium_utils
    from applitools.common.utils.custom_types import AnyWebElement

__all__ = ("SelectorByElement", "SelectorByLocator")


@attr.s
class SelectorByElement(GetSelector):
    EYES_SELECTOR_TAG = "data-eyes-selector"

    _sel = attr.ib()  # type: AnyWebElement

    def get_selector(self, eyes):
        # type: (Eyes) -> Text
        random_id = uuid.uuid4().hex
        element = eyes_selenium_utils.get_underlying_webelement(self._sel)
        eyes.driver.execute_script(
            "arguments[0].setAttribute('{}', '{}');".format(
                self.EYES_SELECTOR_TAG, random_id
            ),
            element,
        )
        return '[{}="{}"]'.format(self.EYES_SELECTOR_TAG, random_id)


@attr.s
class SelectorByLocator(GetSelector):
    _sel = attr.ib()  # type: Text

    def get_selector(self, eyes):
        # type: (Eyes) -> Text
        element = eyes.driver.find_element(self._sel)
        return SelectorByElement(element).get_selector(eyes)
