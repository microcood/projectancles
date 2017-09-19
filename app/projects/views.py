from .models import Project, ProjectType
from rest_utils import create_viewset


class ProjectsViewset(create_viewset(Project, ProjectType)):
    pass
