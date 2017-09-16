from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from apistar import typesystem


class IterableBase():
    typedef = typesystem.Object

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        for c in inspect(self).mapper.column_attrs:
            if c.key in self.__class__.typedef.properties.keys():
                yield (c.key, getattr(self, c.key))


Base = declarative_base(cls=IterableBase)
