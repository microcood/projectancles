from sqlalchemy import Column, Integer, String
from apistar import typesystem
from db_base import Base
from typesystem import ModelType


class ProjectType(ModelType):
    render_fields = ['id', 'name']
    properties = {
        "id": typesystem.integer(default=0),
        "name": typesystem.String
    }


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
