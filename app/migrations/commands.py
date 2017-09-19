import os
from alembic import command
from alembic.config import Config


class MigrationsConfig(Config):
    def get_template_directory(self):
        return os.path.abspath(os.path.dirname(__file__))


config = MigrationsConfig('alembic.ini')
config.set_main_option('script_location', './migrations/dir')


def revision():
    command.revision(config, autogenerate=True)


def upgrade():
    command.upgrade(config, 'head')


def downgrade():
    command.downgrade(config, '-1')
