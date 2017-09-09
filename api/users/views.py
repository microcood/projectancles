from apistar import http
from apistar.backends.sqlalchemy_backend import Session
from apistar.exceptions import NotFound
from .models import User, UserType


async def create_user(data: UserType, session: Session):
    user = User(first_name=data['first_name'], last_name=data['last_name'])
    session.add(user)
    session.commit()
    return http.Response(UserType(user), status=201)


async def get_users_list(session: Session):
    queryset = session.query(User).all()
    return [UserType(user) for user in queryset]


async def get_user(user_id: int, session: Session):
    user = session.query(User).filter(
        User.id == user_id
    ).first()
    if not user:
        raise NotFound()
    return UserType(user)


async def update_user(user_id: int, data: UserType, session: Session):
    user = session.query(User).filter(
        User.id == user_id
    ).first()
    if not user:
        raise NotFound()
    user.first_name = data['first_name']
    session.commit()
    return UserType(user)


async def delete_user(user_id: int, session: Session):
    deleted = session.query(User).filter(
        User.id == user_id
    ).delete()
    if not deleted:
        raise NotFound()
    session.commit()
    return http.Response(status=204)
