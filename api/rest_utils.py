from apistar import http
from apistar.backends.sqlalchemy_backend import Session
from apistar.exceptions import NotFound


def route(url, methods=None, **kwargs):
    methods = ['GET'] if (methods is None) else methods

    def decorator(func):
        func.url = url
        func.http_methods = methods
        func.kwargs = kwargs
        func.is_route = True
        return func
    return decorator


def create_viewset(model, model_type):

    class ApiSet(object):

        @staticmethod
        @route('/')
        async def get_objs_list(session: Session):
            queryset = session.query(model).all()
            return [model_type(obj) for obj in queryset]

        @staticmethod
        @route('/', ['POST'])
        async def create_obj(data: model_type, session: Session):
            obj = model(name=data['name'])
            session.add(obj)
            session.commit()
            return http.Response(model_type(obj), status=201)

        @staticmethod
        @route('/{obj_id}')
        async def get_obj(obj_id: int, session: Session):
            obj = session.query(model).filter(
                model.id == obj_id
            ).first()
            if not obj:
                raise NotFound()
            return model_type(obj)

        @staticmethod
        @route('/{obj_id}', ['PATCH'])
        async def update_obj(obj_id: int, data: model_type, session: Session):
            obj = session.query(model).filter(
                model.id == obj_id
            ).first()
            if not obj:
                raise NotFound()
            obj.name = data['name']
            session.commit()
            return model_type(obj)

        @staticmethod
        @route('/{obj_id}', ['DELETE'])
        async def delete_obj(obj_id: int, session: Session):
            deleted = session.query(model).filter(
                model.id == obj_id
            ).delete()
            if not deleted:
                raise NotFound()
            session.commit()
            return http.Response(status=204)

    return ApiSet()
