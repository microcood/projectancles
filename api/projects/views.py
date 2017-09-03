from apistar import http
from apistar.backends.sqlalchemy_backend import Session
from apistar.exceptions import NotFound
from .models import Project, ProjectType


def create_project(data: ProjectType, session: Session):
    project = Project(name=data['name'])
    session.add(project)
    session.commit()
    return http.Response(ProjectType(project), status=201)


def get_projects_list(session: Session):
    queryset = session.query(Project).all()
    return [ProjectType(project) for project in queryset]


def get_project(project_id: int, session: Session):
    project = session.query(Project).filter(
        Project.id == project_id
    ).first()
    if not project:
        raise NotFound()
    return ProjectType(project)


def update_project(project_id: int, data: ProjectType, session: Session):
    project = session.query(Project).filter(
        Project.id == project_id
    ).first()
    if not project:
        raise NotFound()
    project.name = data['name']
    session.commit()
    return ProjectType(project)


def delete_project(project_id: int, session: Session):
    deleted = session.query(Project).filter(
        Project.id == project_id
    ).delete()
    if not deleted:
        raise NotFound()
    session.commit()
    return http.Response(status=204)
