from .models import Project
from apistar.test import TestClient
from apistar.backends.sqlalchemy_backend import Session


def test_projects_list_empty(session: Session, client: TestClient):
    response = client.get('/projects/')
    assert response.status_code == 200
    assert response.json() == []


def test_projects_list(session: Session, client: TestClient):
    project = Project(name='asdf')
    session.add(project)
    session.commit()

    project2 = Project(name='asdf2')
    session.add(project2)
    session.commit()

    response = client.get('/projects/')
    assert response.status_code == 200
    assert response.json() == [{
        "id": project.id,
        "name": project.name
    }, {
        "id": project2.id,
        "name": project2.name
    }]


def test_project_create(session: Session, client: TestClient):
    response = client.post('/projects/', data={
        "name": "project 7776776"
    })

    project = session.query(Project).filter(
        Project.name == "project 7776776"
    ).order_by(Project.id.desc()).first()

    assert response.status_code == 201
    assert response.json() == {
        "id": project.id,
        "name": project.name
    }


def test_project_view(session: Session, client: TestClient):
    project = Project(name='asdf34534')
    session.add(project)
    session.commit()

    response = client.get('/projects/{}'.format(project.id))
    assert response.status_code == 200
    assert response.json() == {
        "id": project.id,
        "name": project.name
    }


def test_project_delete(session: Session, client: TestClient):
    project = Project(name='asdf78')
    session.add(project)
    session.commit()

    query = session.query(Project).filter(
        Project.id == project.id
    )
    assert query.count() == 1

    response = client.delete('/projects/{}'.format(project.id))

    assert response.status_code == 204
    assert response.text == ""
    assert query.count() == 0


def test_project_update(session: Session, client: TestClient):
    project = Project(name='asdf754')
    session.add(project)
    session.commit()

    response = client.patch('/projects/{}'.format(project.id), data={
        "name": "project's new name"
    })

    session.refresh(project)
    assert response.status_code == 200
    assert response.json() == {
        "id": project.id,
        "name": "project's new name"
    }
    assert project.name == "project's new name"


def test_project_not_exists(client: TestClient):
    res = client.get('/projects/8884444')
    res1 = client.patch('/projects/8884444')
    res2 = client.delete('/projects/8884444')

    assert res.status_code == res1.status_code == res2.status_code == 404
    assert res.json() == res1.json() == res2.json() == {"message": "Not found"}
