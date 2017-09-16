from .models import User, UserType
from rest_utils import create_viewset
from apistar import http
from apistar.backends.sqlalchemy_backend import Session
from rest_utils import route
from werkzeug.security import generate_password_hash


class UsersViewSet(create_viewset(User, UserType)):

    @route('/', ['POST'])
    async def create_obj(data: UserType, session: Session):
        data.pop('id')
        obj = User(**data)
        obj.password = generate_password_hash(obj.password)
        session.add(obj)
        session.commit()
        return http.Response(UserType(obj), status=201)
