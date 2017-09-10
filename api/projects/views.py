from .models import Project, ProjectType
from rest_utils import create_viewset


projects_viewset = create_viewset(Project, ProjectType)
