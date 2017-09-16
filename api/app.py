import os
from apistar import Include, Command
from apistar.backends import sqlalchemy_backend
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls
from projects.views import ProjectsViewset
from users.views import UsersViewSet
from rest_utils import register_urls
from db_base import Base
from apistar.backends.sqlalchemy_backend import SQLAlchemyBackend
from utils import get_component
from server import run


settings = {
    "DATABASE": {
        "URL": 'postgresql://{e[DB_USER]}:{e[DB_PASSWORD]}@{e[DB_HOST]}/{e[DB_NAME]}'  # nopep8
               .format(e=os.environ),
        "METADATA": Base.metadata
    }
}


routes = [
    register_urls('/projects', ProjectsViewset),
    register_urls('/users', UsersViewSet),
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]


app = App(
    settings=settings,
    routes=routes,
    commands=sqlalchemy_backend.commands + [Command('run', run)],
    components=sqlalchemy_backend.components
)

backend = get_component(SQLAlchemyBackend)
Base.metadata.create_all(backend.engine)


if __name__ == '__main__':
    app.main()
