from apistar.backends.sqlalchemy_backend import Session
from .models import Project
from utils import get_component


def create_project(name: str):
    session = get_component(Session)
    project = Project(name=name)
    session.add(project)
    session.commit()
    return {
        'id': project.id,
        'name': project.name
    }


def get_projects_list():
    session = get_component(Session)
    queryset = session.query(Project).all()
    return [
        {'id': project.id, 'name': project.name}
        for project in queryset
    ]


def get_project(project_id: int):
    session = get_component(Session)
    project = session.query(Project).filter(
        Project.id == project_id
    ).first()
    return {
        'id': project.id,
        'name': project.name
    }
