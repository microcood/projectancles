from sqlalchemy import Column, Integer, String
from apistar import typesystem
from db_base import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class ProjectType(typesystem.Object):
    properties = {
        "id": typesystem.Integer,
        "name": typesystem.String
    }
