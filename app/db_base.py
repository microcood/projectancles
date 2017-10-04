from apistar import typesystem
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base


class BaseScheme(typesystem.Object):
    render_fields = []
    properties = {}


class IterableBase():
    _scheme = BaseScheme

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        for c in inspect(self).mapper.column_attrs:
            yield (c.key, getattr(self, c.key))

    def render(self):
        obj = self._scheme(dict(self))
        return {k: obj[k] for k in self._scheme.render_fields}


Base = declarative_base(cls=IterableBase)
