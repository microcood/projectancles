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

from app import app
from db_base import Base
from utils import get_component

from users.models import User
from projects.models import Project
from apistar.test import TestClient
from apistar.backends.sqlalchemy_backend import Session


fake = Faker()


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


@pytest.fixture(scope='session')
def anon_client():
    return TestClient(app)


@pytest.fixture(scope='session')
def client():
    clnt = TestClient(app)
    settings = get_component(Settings)
    token = jwt.encode(
        {'user_id': 1234}, settings['JWT_SECRET'], algorithm='HS256')
    clnt.headers.update(
        {'Authorization': 'Bearer {}'.format(token.decode('utf-8'))})
    print(clnt.headers)
    return clnt


class BaseTestViewSet(object):
    def mock_obj(self):
        return {}

    def create_obj(self, session):
        obj = self.model(**self.mock_obj())
        session.add(obj)
        session.commit()
        return obj

    def test_list_empty(self, session: Session, client: TestClient):
        response = client.get('/{}/'.format(self.url))
        assert response.status_code == 200
        assert response.json() == []

    def test_list(self, session: Session, client: TestClient):
        obj = self.create_obj(session)
        obj2 = self.create_obj(session)

        response = client.get('/{}/'.format(self.url))

        assert response.status_code == 200
        assert response.json() == [
            obj.render(),
            obj2.render()
        ]

    def test_create(self, session: Session, client: TestClient):
        fake_obj = self.mock_obj()
        response = client.post(
            '/{}/'.format(self.url),
            data=fake_obj
        )

        resp_obj = response.json()

        obj = session.query(self.model).filter(
            self.model.id == resp_obj['id']
        ).first()

        assert response.status_code == 201
        assert response.json() == obj.render()

    def test_view_one(self, session: Session, client: TestClient):
        obj = self.create_obj(session)

        response = client.get('/{}/{}'.format(self.url, obj.id))
        assert response.status_code == 200
        assert response.json() == obj.render()

    def test_delete(self, session: Session, client: TestClient):
        obj = self.create_obj(session)

        query = session.query(self.model).filter(
            self.model.id == obj.id
        )

        response = client.delete('/{}/{}'.format(self.url, obj.id))

        assert response.status_code == 204
        assert response.text == ""
        assert query.count() == 0

    def test_update(self, session: Session, client: TestClient):
        obj = self.create_obj(session)

        new_mock = self.mock_obj()
        response = client.patch(
            '/{}/{}'.format(self.url, obj.id),
            data=new_mock
        )

        new_obj = dict(obj)
        for k in new_obj.keys():
            if new_mock.get(k):
                new_obj[k] = new_mock.get(k)

        session.refresh(obj)
        assert dict(obj) == new_obj
        assert response.status_code == 200
        assert response.json() == obj.render()

    def test_nonexistance(self, client: TestClient):
        res = client.get('/{}/{}'.format(self.url, 12344123))
        res1 = client.patch('/{}/{}'.format(self.url, 12344123))
        res2 = client.delete('/{}/{}'.format(self.url, 12344123))

        assert res.status_code == res1.status_code == res2.status_code == 404
        assert res.json() == res1.json() == res2.json() == {
            "message": "Not found"
        }


class TestUserViewSet(BaseTestViewSet):
    url = 'users'
    model = User

    def mock_obj(self):
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "password": fake.password(),
            "email": fake.email()
        }

    def test_password(self, session: Session, client: TestClient):
        from werkzeug.security import check_password_hash

        fake_obj = self.mock_obj()
        response = client.post(
            '/{}/'.format(self.url),
            data=fake_obj
        )
        user_obj = response.json()
        user = session.query(User).filter(User.id == user_obj['id']).first()
        assert check_password_hash(str(user.password), fake_obj['password'])

    def test_password_not_exposed(self, session: Session, client: TestClient):
        obj = self.create_obj(session)
        response = client.get('/{}/{}'.format(self.url, obj.id))
        resp_obj = response.json()
        assert not resp_obj.get('password')

    # def test_django_password_validation(self)


class TestProjectsViewSet(BaseTestViewSet):
    url = 'projects'
    model = Project

    def mock_obj(self):
        return {
            "name": fake.word(),
        }


def test_token(session: Session, client: TestClient):
    settings = get_component(Settings)
    JWT_SECRET = settings['JWT_SECRET']

    user = TestUserViewSet().create_obj(session)

    response = client.post('/tokens/', data={
        "grant_type": "password",
        "username": user.email,
        "password": user.password,
    })
    response_dict = response.json()
    jwt_payload = jwt.decode(
        response_dict['access_token'], JWT_SECRET, algorithms=['HS256'])

    assert response.status_code == 200
    assert jwt_payload == {
        "user_id": user.id,
        "exp": response_dict['expires_in']
    }
    assert response_dict['expires_in'] > int(datetime.now().timestamp())


def test_authorization_flow(session: Session, anon_client: TestClient):
    user = TestUserViewSet().create_obj(session)
    response = anon_client.get('/projects/')

    assert response.status_code == 401
    assert response.json() == {"message": "Not authenticated"}

    response = anon_client.post('/tokens/', data={
        "grant_type": "password",
        "username": user.email,
        "password": user.password,
    })

    token = response.json().get('access_token')
    anon_client.headers.update(
        {'Authorization': 'Bearer {}'.format(token)})

    response = anon_client.get('/projects/')
    assert response.status_code == 200
    assert type(response.json()) == list
