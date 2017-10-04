from .models import Project
from apistar import http, Include, Route
from apistar.interfaces import Auth
from apistar.backends.sqlalchemy_backend import Session
from rest_utils import common_routes


async def create_project(data: Project._scheme, auth: Auth, session: Session):
    data.pop('id')
    obj = Project(**data)
    obj.user_id = auth.get_user_id()
    session.add(obj)
    session.commit()
    return http.Response(obj.render(), status=201)


routes = Include('/projects', [
    Route('/', 'POST', create_project),
] + common_routes(Project, exclude=['create_route']))
