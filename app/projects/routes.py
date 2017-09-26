from .models import Project
from apistar import Include
from rest_utils import common_routes


routes = Include('/projects', common_routes(Project))
