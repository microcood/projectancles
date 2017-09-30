import os
import pytest
from datetime import datetime

import jwt
from faker import Faker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from apistar import Settings
from apistar.backends.sqlalchemy_backend import SQLAlchemyBackend
from apistar.test import TestClient
from apistar.backends.sqlalchemy_backend import Session
from werkzeug.security import check_password_hash

from app import app
from db_base import Base
from utils import get_component
from users.models import User
from projects.models import Project


fake = Faker()


@pytest.fixture(scope='session')
def settings():
    return get_component(Settings)


@pytest.fixture(scope='session')
def session(request):
    backend = get_component(SQLAlchemyBackend)

    try:
        conn = backend.engine.connect()
        conn.execute("COMMIT")
        conn.execute("CREATE DATABASE test_database")
        conn.close()
    except Exception as e:
        pass

    engine_new = create_engine(
        'postgresql://{e[DB_USER]}:{e[DB_PASSWORD]}@{e[DB_HOST]}/test_database'  # nopep8
        .format(e=os.environ),
        poolclass=NullPool
    )

    backend.engine = engine_new
    backend.Session = sessionmaker(bind=engine_new)
    Base.metadata.create_all(engine_new)
    session = backend.Session()

    def teardown():
        session.close_all()
        Base.metadata.drop_all(engine_new)

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def anon_client():
    return TestClient(app)


@pytest.fixture(scope='session')
def client(settings):
    clnt = TestClient(app)
    token = jwt.encode(
        {'user_id': 1234}, settings['JWT_SECRET'], algorithm='HS256')
    clnt.headers.update(
        {'Authorization': 'Bearer {}'.format(token.decode('utf-8'))})
    return clnt


class BaseTestViewSet(object):
    def _mock_obj(self):
        return {}

    def _create_obj(self, session):
        obj = self.model(**self._mock_obj())
        session.add(obj)
        session.commit()
        return obj

    @pytest.fixture(scope='function')
    def new_obj(self, session: Session):
        return self._create_obj(session)

    @pytest.fixture(scope='function')
    def mock(self):
        return self._mock_obj()

    @pytest.fixture(scope='function')
    def clean_db(self, session):
        session.query(self.model).delete()
        session.commit()

    def test_list(self, session: Session, client: TestClient):
        obj = self._create_obj(session)
        obj2 = self._create_obj(session)

        response = client.get('/{}/'.format(self.url))

        assert response.status_code == 200
        assert response.json() == [
            obj.render(),
            obj2.render()
        ]

    def test_list_empty(self, clean_db, client: TestClient):
        response = client.get('/{}/'.format(self.url))

        assert response.status_code == 200
        assert response.json() == []

    def test_create(self, mock: dict, session: Session, client: TestClient):
        response = client.post(
            '/{}/'.format(self.url),
            data=mock
        )
        resp_obj = response.json()
        obj = session.query(self.model).filter_by(id=resp_obj['id']).first()

        assert response.status_code == 201
        assert response.json() == obj.render()

    def test_view_one(self, new_obj: Base, client: TestClient):
        response = client.get('/{}/{}'.format(self.url, new_obj.id))

        assert response.status_code == 200
        assert response.json() == new_obj.render()

    def test_delete(self, new_obj: Base, session: Session, client: TestClient):
        query = session.query(self.model).filter_by(id=new_obj.id)
        response = client.delete('/{}/{}'.format(self.url, new_obj.id))

        assert response.status_code == 204
        assert response.text == ""
        assert query.count() == 0

    def test_update(
        self,
        new_obj: Base,
        mock: dict,
        session: Session,
        client: TestClient
    ):
        response = client.patch(
            '/{}/{}'.format(self.url, new_obj.id),
            data=mock
        )

        mock['id'] = new_obj.id
        session.refresh(new_obj)

        assert response.status_code == 200
        assert response.json() == self.model(**mock).render()
        assert response.json() == new_obj.render()

    @pytest.mark.parametrize("method, id", [
        ("GET", 3),
        ("PATCH", 3),
        ("DELETE", 3),
    ])
    def test_not_found(self, clean_db, client: TestClient, method, id):
        res = client.request(method, '/{}/{}'.format(self.url, id))

        assert res.status_code == 404
        assert res.json() == {"message": "Not found"}

    @pytest.mark.parametrize("method, url", [
        ("GET", '/{}/3'),
        ("POST", '/{}/'),
        ("PATCH", '/{}/3'),
        ("DELETE", '/{}/3'),
    ])
    def test_not_authenticated(self, anon_client: TestClient, method, url):
        res = anon_client.request(method, url.format(self.url))

        assert res.status_code == 401
        assert res.json() == {"message": "Not authenticated"}


class TestUserViewSet(BaseTestViewSet):
    url = 'users'
    model = User

    def _mock_obj(self):
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": fake.password(),
            "email": fake.email()
        }

    def test_password(self, mock, session: Session, client: TestClient):
        response = client.post(
            '/{}/'.format(self.url),
            data=mock
        )
        user_obj = response.json()
        user = session.query(User).filter_by(id=user_obj['id']).first()

        assert check_password_hash(str(user.password), mock['password'])

    def test_password_not_exposed(self, new_obj, client: TestClient):
        response = client.get('/{}/{}'.format(self.url, new_obj.id))

        assert not response.json().get('password')

    def test_user_bound_token(
        self,
        settings: Settings,
        new_obj: Base,
        client: TestClient
    ):
        response = client.post('/tokens/', data={
            "grant_type": "password",
            "username": new_obj.email,
            "password": new_obj.password,
        })
        response_dict = response.json()
        jwt_payload = jwt.decode(
            response_dict['access_token'],
            settings['JWT_SECRET'],
            algorithms=['HS256']
        )

        assert response.status_code == 200
        assert jwt_payload == {
            "user_id": new_obj.id,
            "exp": response_dict['expires_in']
        }
        assert response_dict['expires_in'] > int(datetime.now().timestamp())

    def test_authorization_flow(
        self,
        new_obj: Base,
        session: Session,
        anon_client: TestClient
    ):
        response1 = anon_client.get('/projects/')
        response2 = anon_client.post('/tokens/', data={
            "grant_type": "password",
            "username": new_obj.email,
            "password": new_obj.password,
        })
        token = response2.json().get('access_token')
        anon_client.headers.update({
            'Authorization': 'Bearer {}'.format(token)
        })
        response3 = anon_client.get('/projects/')

        assert response1.status_code == 401
        assert response2.status_code == 200
        assert response3.status_code == 200


class TestProjectsViewSet(BaseTestViewSet):
    url = 'projects'
    model = Project

    def _mock_obj(self):
        return {
            "name": fake.word(),
        }
