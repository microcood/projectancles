from datetime import datetime, timedelta
import jwt
from apistar import annotate, http, typesystem, Route, Include, Settings
from apistar.backends.sqlalchemy_backend import Session
from apistar.authentication import Authenticated
from apistar.exceptions import HTTPException, BadRequest
from users.models import User


class LoginData(typesystem.Object):
    properties = {
        'grant_type': typesystem.String,
        'username': typesystem.String,
        'password': typesystem.String,
    }


class Unauthorized(HTTPException):
    default_status_code = 401
    default_detail = 'Not authenticated'


class TokenAuthentication():
    def authenticate(self, authorization: http.Header, settings: Settings):
        if not authorization:
            raise Unauthorized()
        scheme, token = authorization.split()
        try:
            payload = jwt.decode(
                token, settings['JWT_SECRET'], algorithms=['HS256'])
            return Authenticated(payload['user_id'])
        except jwt.exceptions.InvalidTokenError:
            raise Unauthorized()


@annotate(permissions=[])
async def create_token(
    data: LoginData,
    session: Session,
    settings: Settings
):
    user = session.query(User).filter_by(email=data['username']).first()
    if not user or not user.password == data['password']:
        raise BadRequest({"message": "Email and password do not match"})
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
