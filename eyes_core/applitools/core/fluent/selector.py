import typing

import attr

if typing.TYPE_CHECKING:
    from typing import Text
    from applitools.core.eyes_base import EyesBase


@attr.s
class GetSelector(object):
    _sel = attr.ib()

    def get_selector(self, eyes):
        # type: (EyesBase) -> Text
        return self._sel
