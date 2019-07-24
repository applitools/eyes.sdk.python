from typing import TYPE_CHECKING, Text

import attr

if TYPE_CHECKING:
    from applitools.core import EyesBase


@attr.s
class GetSelector(object):
    _sel = attr.ib()  # type: Text

    def get_selector(self, eyes):
        # type: (EyesBase) -> Text
        return self._sel
