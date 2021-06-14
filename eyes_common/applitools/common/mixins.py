import attr


class DictAccessMixin(object):
    """Make dict-like object from attrs class"""

    def __getitem__(self, item):
        fields = [a.name for a in attr.fields(self.__class__)]
        if isinstance(item, int):
            item = fields[item]
        if item not in fields:
            raise KeyError("item: {}, fields: {}".format(item, fields))
        return getattr(self, item)
