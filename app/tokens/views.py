from apistar import http, Route, Include
from apistar.backends.sqlalchemy_backend import Session


async def get_objs_list(session: Session):
    return http.Response({
        "hello": 12342
    })


async def create_obj(data, session: Session):
    # data.pop('id')
    # obj = model(**data)
    # session.add(obj)
    # session.commit()
    return http.Response({
        "hello": 12342
    })


def create_view(name):
    async def func(data, session: Session):
        return http.Response({
            "hello": name + '12342'
        })
    return Route('/', 'GET', func, name="create_{}".format(name))


routes = Include('/tokens', [
    # Route('/', 'GET', get_objs_list),
    create_view('papa'),
    create_view('mama'),

    # Route('/', 'POST', create_obj)
])

