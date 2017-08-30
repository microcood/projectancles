from .models import Project
from apistar.test import TestClient
from apistar.backends.sqlalchemy_backend import Session


def test_projects_list_empty(session: Session, client: TestClient):
    response = client.get('/projects')
    assert response.status_code == 200
    assert response.json() == []


def test_projects_list(session: Session, client: TestClient):
    project = Project(name='asdf')
    session.add(project)
    session.commit()

    response = client.get('/projects')
    assert response.status_code == 200
    assert response.json() == [{
        "id": project.id,
        "name": project.name
    }]
