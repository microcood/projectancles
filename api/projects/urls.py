from apistar import Route
from .views import projects_viewset
# from . import views

projects_urls = []

for methodname in dir(projects_viewset):
    method = getattr(projects_viewset, methodname)
    is_route = getattr(method, 'is_route', False)
    if is_route:
        http_methods = getattr(method, 'http_methods')
        url = getattr(method, 'url')
        for http_method in http_methods:
            projects_urls.append(Route(url, http_method, method))
