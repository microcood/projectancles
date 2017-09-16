from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base

class IterableBase():
    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        for c in inspect(self).mapper.column_attrs:
            yield (c.key, getattr(self, c.key))


Base = declarative_base(cls=IterableBase)
