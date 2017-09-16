import os
import pytest

from faker import Faker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

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
def client():
    return TestClient(app)


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
        assert response.json() == [dict(obj), dict(obj2)]

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
        assert response.json() == dict(obj)

    def test_view_one(self, session: Session, client: TestClient):
        obj = self.create_obj(session)

        response = client.get('/{}/{}'.format(self.url, obj.id))
        assert response.status_code == 200
        assert response.json() == dict(obj)

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
        assert response.json() == dict(obj)

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
        }


class TestProjectsViewSet(BaseTestViewSet):
    url = 'projects'
    model = Project

    def mock_obj(self):
        return {
            "name": fake.word(),
        }
