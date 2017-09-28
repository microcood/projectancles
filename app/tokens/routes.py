from datetime import datetime, timedelta
import jwt
from apistar import typesystem, Route, Include, Settings
from apistar.backends.sqlalchemy_backend import Session
from users.models import User


class LoginData(typesystem.Object):
    properties = {
        'grant_type': typesystem.String,
        'username': typesystem.String,
        'password': typesystem.String,
    }


async def create_token(
    data: LoginData,
    session: Session,
    settings: Settings
):
    user = session.query(User).filter_by(email=data['username']).first()
    expires = (datetime.now() + timedelta(days=5)).timestamp()
    token = jwt.encode(
        {'user_id': user.id, 'exp': int(expires)},
        settings['JWT_SECRET'],
        algorithm='HS256'
    )

    return {
        'token_type': 'Bearer',
        'access_token': token.decode('utf-8'),
        'expires_in': int(expires),
    }


routes = Include('/tokens', [
    Route('/', 'POST', create_token)
])
