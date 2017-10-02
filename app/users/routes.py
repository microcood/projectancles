from .models import User
from apistar import http, Include, Route
from apistar.backends.sqlalchemy_backend import Session
from rest_utils import common_routes


async def create_user(data: User._scheme, session: Session):
    data.pop('id')
    obj = User(**data)
    session.add(obj)
    session.commit()
    return http.Response(obj.render(), status=201)


routes = Include('/users', [
    Route('/', 'POST', create_user),
] + common_routes(User, exclude=['create_route']))
