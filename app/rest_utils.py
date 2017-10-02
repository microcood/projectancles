import re
from sqlalchemy import or_
from apistar import http, Route
from apistar.backends.sqlalchemy_backend import Session
from apistar.exceptions import NotFound, BadRequest
from apistar import typesystem


class Filters(typesystem.String):
    operator_map = {
        '==': '__eq__',
        '!=': '__ne__',
        '>': '__gt__',
        '<': '__lt__',
        '>=': '__ge__',
        '<=': '__le__',
        '~contains~': 'contains',
    }
    description = (
        "comparison operators: {}".format(" , ".join(operator_map.keys()))
    )

    def __new__(cls, *args, **kwargs):
        data = super().__new__(cls, *args, **kwargs)

        pairs = data.split(',')
        expressions = []

        for pair in pairs:
            # finds comparison operators or anything between `~`
            op = re.search(r'(>(=)?)|(<(=)?)|(==)|(!=)|~(.*)~', pair)
            try:
                operator = cls.operator_map.get(op.group())
                field_name, value = pair.split(op.group())
                column = getattr(cls.model, field_name)
                comparator = getattr(column, operator)
                expressions.append(comparator(value))
            except AttributeError:
                raise BadRequest()
        return expressions


class Ordering(typesystem.String):
    description = "prepend field name with `-` to descend"

    def __new__(cls, *args, **kwargs):
        data = super().__new__(cls, *args, **kwargs)

        expression = None
        order = "desc" if data.startswith('-') else "asc"

        try:
            field_name = re.sub(r'^-', '', data)
            column = getattr(cls.model, field_name)
            expression = getattr(column, order)
        except AttributeError:
            raise BadRequest()
        return expression


def bind(cls, model):
    cls.model = model
    return cls


def list_route(model):
    async def func(
        session: Session,
        filters: bind(Filters, model),
        ordering: bind(Ordering, model),
        query_params: http.QueryParams
    ):
        queryset = session.query(model)
        if filters:
            queryset = queryset.filter(or_(*filters))
        if ordering:
            queryset = queryset.order_by(ordering())
        return [obj.render() for obj in queryset]
    return Route(
        '/', 'GET', func, name="list_{}s".format(model.__name__.lower()))


def create_route(model):
    async def func(data: model._scheme, session: Session):
        data.pop('id')
        obj = model(**data)
        session.add(obj)
        session.commit()
        return http.Response(obj.render(), status=201)
    return Route(
        '/', 'POST', func, name="create_{}".format(model.__name__.lower()))


def view_route(model):
    async def func(id: int, session: Session):
        obj = session.query(model).filter(
            model.id == id
        ).first()
        if not obj:
            raise NotFound()
        return obj.render()
    return Route(
        '/{id}',
        'GET', func, name="view_{}".format(model.__name__.lower()))


def update_route(model):
    async def func(
        id: int,
        data: model._scheme,
        session: Session
    ):
        if data:
            data.pop('id')
        obj = session.query(model).filter(
            model.id == id
        ).first()
        if not obj:
            raise NotFound()
        for key, value in data.items():
            setattr(obj, key, value)
        session.commit()
        return obj.render()
    return Route(
        '/{id}',
        'PATCH', func, name="update_{}".format(model.__name__.lower()))


def delete_route(model):
    async def func(id: int, session: Session):
        deleted = session.query(model).filter(
            model.id == id
        ).delete()
        if not deleted:
            raise NotFound()
        session.commit()
        return http.Response(status=204)
    return Route(
        '/{id}',
        'DELETE', func, name="delete_{}".format(model.__name__.lower()))


def common_routes(model, exclude=[]):
    return [func(model) for func in [
        list_route, create_route, view_route, update_route, delete_route]
        if func.__name__ not in exclude
    ]
