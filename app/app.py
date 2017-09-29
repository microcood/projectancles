import os
from apistar import Include, Command
from apistar.backends import sqlalchemy_backend
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls
from apistar.permissions import IsAuthenticated
from projects.routes import routes as projects_routes
from users.routes import routes as users_routes
from tokens.routes import routes as tokens_routes
from db_base import Base
from server import run
from migrations.commands import revision, upgrade, downgrade
from tokens.routes import TokenAuthentication


settings = {
    "AUTHENTICATION": [TokenAuthentication()],
    "PERMISSIONS": [IsAuthenticated()],
    "JWT_SECRET": os.environ['JWT_SECRET'],
    "DATABASE": {
        "URL": 'postgresql://{e[DB_USER]}:{e[DB_PASSWORD]}@{e[DB_HOST]}/{e[DB_NAME]}'  # nopep8
               .format(e=os.environ),
        "METADATA": Base.metadata
    }
}


routes = [
    users_routes,
    projects_routes,
    tokens_routes,
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]


app = App(
    settings=settings,
    routes=routes,
    commands=sqlalchemy_backend.commands + [
        Command('run', run),
        Command('make_migrations', revision),
        Command('migrate', upgrade),
        Command('revert_migrations', downgrade),
    ],
    components=sqlalchemy_backend.components
)


if __name__ == '__main__':
    app.main()
