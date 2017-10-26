# coding:utf-8
import __builtin__


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]


class Enum(object):

    def __init__(self, *items):
        self.data = AttributeDict()
        self.data.index = 0
        self.data.item = items[0]
        self.data.items_tuple = items

    def __int__(self):
        return self.data.index

    def __float__(self):
        return float(self.data.index)

    def __str__(self):
        return self.data.item

    def __getitem__(self, index):
        enum = Enum(*self.data.items_tuple)
        enum.data.index = index
        enum.data.item = self.data.items_tuple[index]
        return enum

    def __getattr__(self, item):
        enum = Enum(*self.data.items_tuple)
        enum.data.item = item
        enum.data.index = self.data.items_tuple.index(item)
        return enum

    def __cmp__(self, other):
        if isinstance(other, (float, int)) :
            return cmp(int(self), other)
        elif isinstance(other, (str, unicode)):
            return cmp(str(self), other)
        elif isinstance(other, Enum):
            return cmp(str(self), other)
        elif hasattr(other, "__int__") or hasattr(other, "__float__"):
            return cmp(int(self), int(other))
        return cmp(str(self), other)

    def __repr__(self):
        return 'enum(items)[{index}]'.format(items=str(self.data.items_tuple)[1:-2])


__builtin__.enum = Enum
Window = __import__("QFn.window", globals(), locals(), ["Window"], -1).Window
