from apistar import http, Route, Include
from apistar.backends.sqlalchemy_backend import Session
from apistar.exceptions import NotFound


def register_urls(name, viewset):
    object_urls = []
    for methodname, method in viewset.items():
        method.__name__ = methodname
        http_methods = getattr(method, 'http_methods')
        url = getattr(method, 'url')
        for http_method in http_methods:
            object_urls.append(Route(url, http_method, method))
    return Include(name, object_urls)


def route(url, methods=None, **kwargs):
    methods = ['GET'] if (methods is None) else methods

    def decorator(func):
        func.url = url
        func.http_methods = methods
        func.kwargs = kwargs
        return func
    return decorator


def create_viewset(model, model_type):
    @route('/')
    async def get_objs_list(session: Session):
        queryset = session.query(model).all()
        return [model_type(obj) for obj in queryset]

    @route('/', ['POST'])
    async def create_obj(data: model_type, session: Session):
        data.pop('id')
        obj = model(**data)
        session.add(obj)
        session.commit()
        return http.Response(model_type(obj), status=201)

    @route('/{obj_id}')
    async def get_obj(obj_id: int, session: Session):
        obj = session.query(model).filter(
            model.id == obj_id
        ).first()
        if not obj:
            raise NotFound()
        return model_type(obj)

    @route('/{obj_id}', ['PATCH'])
    async def update_obj(obj_id: int, data: model_type, session: Session):
        if data:
            data.pop('id')
        obj = session.query(model).filter(
            model.id == obj_id
        ).first()
        if not obj:
            raise NotFound()
        for key, value in data.items():
            setattr(obj, key, value)
        session.commit()
        return model_type(obj)

    @route('/{obj_id}', ['DELETE'])
    async def delete_obj(obj_id: int, session: Session):
        deleted = session.query(model).filter(
            model.id == obj_id
        ).delete()
        if not deleted:
            raise NotFound()
        session.commit()
        return http.Response(status=204)

    object_name = model.__name__.lower()
    return {
        'get_{}_list'.format(object_name): get_objs_list,
        'create_{}'.format(object_name): create_obj,
        'get_{}'.format(object_name): get_obj,
        'update_{}'.format(object_name): update_obj,
        'delete_{}'.format(object_name): delete_obj
    }
