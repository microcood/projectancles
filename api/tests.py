import os
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from apistar.backends.sqlalchemy_backend import SQLAlchemyBackend

from app import app
from db_base import Base
from utils import get_component


from projects.tests import *


def create_test_db(engine):
    conn = engine.connect()
    conn.execute("COMMIT")
    conn.execute("CREATE DATABASE test_database")
    conn.close()


def remove_test_db(engine):
    conn = engine.connect()
    conn.execute("COMMIT")
    conn.execute("DROP DATABASE test_database")
    conn.close()


@pytest.fixture(scope='session')
def session(request):
    backend = get_component(SQLAlchemyBackend)
    engine = backend.engine
    try:
        create_test_db(engine)
    except Exception as e:
        remove_test_db(engine)
        create_test_db(engine)

    engine_new = create_engine(
        'postgresql://{e[DB_USER]}:{e[DB_PASSWORD]}@{e[DB_HOST]}/test_database'  # nopep8
        .format(e=os.environ),
        poolclass=NullPool
    )

    backend.engine = engine_new
    backend.Session = sessionmaker(bind=engine_new)
    Base.metadata.create_all(engine_new)
    # session = backend.Session()

    def teardown():
        try:
            remove_test_db(engine)
        except Exception as e:
            pass

    request.addfinalizer(teardown)
    return backend.Session()


@pytest.fixture(scope='session')
def client():
    return TestClient(app)
