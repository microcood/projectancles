from apistar import Route
from . import views

projects_urls = [
    Route('/', 'GET', views.projects_list),
    Route('/{project_id}', 'GET', views.project_view),
]