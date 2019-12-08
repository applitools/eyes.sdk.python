class DictAccessMixin(object):
    """Make dict-like object from attrs class"""

    def __getitem__(self, item):
        if isinstance(item, int):
            item = self.__slots__[item]
        if item not in self.__slots__:
            raise KeyError
        return getattr(self, item)
