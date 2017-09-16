from sqlalchemy import Column, Integer, String
from apistar import typesystem
from db_base import Base


class ProjectType(typesystem.Object):
    properties = {
        "id": typesystem.integer(default=0),
        "name": typesystem.String
    }

class Project(Base):
    __tablename__ = "projects"
    typedef = ProjectType

    id = Column(Integer, primary_key=True)
    name = Column(String)
