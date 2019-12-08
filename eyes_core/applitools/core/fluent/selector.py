from typing import TYPE_CHECKING, Any

import attr

if TYPE_CHECKING:
    from applitools.core import EyesBase


@attr.s
class GetSelector(object):
    _sel = attr.ib()  # type: Any

    def get_selector(self, eyes):
        # type: (EyesBase) -> Any
        return self._sel
