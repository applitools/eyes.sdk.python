import attr


@attr.s
class GetSelector(object):
    _sel = attr.ib()

    def get_selector(self, eyes):
        return self._sel
