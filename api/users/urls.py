from apistar import Route
from . import views

users_urls = [
    Route('/', 'GET', views.get_users_list),
    Route('/', 'POST', views.create_user),
    Route('/{user_id}', 'GET', views.get_user),
    Route('/{user_id}', 'PATCH', views.update_user),
    Route('/{user_id}', 'DELETE', views.delete_user),
]
