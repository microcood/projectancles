from apistar import http
from apistar.backends.sqlalchemy_backend import Session
from .models import Project, ProjectType
from utils import get_component


def create_project(data: http.RequestData):
    session = get_component(Session)
    project = Project(name=data['name'])
    session.add(project)
    session.commit()
    return http.Response({
        "id": project.id,
        "name": project.name
    }, status=201)


def get_projects_list():
    session = get_component(Session)
    queryset = session.query(Project).all()
    return [ProjectType(project) for project in queryset]


def get_project(project_id: int):
    session = get_component(Session)
    project = session.query(Project).filter(
        Project.id == project_id
    ).first()
    return ProjectType(project)


def update_project(project_id: int, data: http.RequestData):
    session = get_component(Session)
    project = session.query(Project).filter(
        Project.id == project_id
    ).first()

    project.name = data['name']
    session.commit()
    return {
        "id": project.id,
        "name": project.name
    }


def delete_project(project_id: int):
    session = get_component(Session)
    session.query(Project).filter(
        Project.id == project_id
    ).delete()
    session.commit()
    return http.Response(status=204)
