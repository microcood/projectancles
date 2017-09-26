from apistar import http, Route
from apistar.backends.sqlalchemy_backend import Session
from apistar.exceptions import NotFound


def list_route(model):
    async def func(session: Session):
        queryset = session.query(model).all()
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
