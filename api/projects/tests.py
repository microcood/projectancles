import pytest
from app import app
from apistar.test import TestClient


@pytest.fixture()
def client():
    return TestClient(app)


def test_projects_list(client: TestClient):
    response = client.get('/projects')
    assert response.status_code == 200
    assert response.json() == [{'name': 'Hello'}]


def test_project_view(client: TestClient):
    response = client.get('/projects/1')
    assert response.status_code == 200
    assert response.json() == {'name': 'Hello'}

