from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from apistar import typesystem
from db_base import Base, BaseScheme


class NullableInt(typesystem.Integer):
    def __new__(cls, *args, **kwargs):
        if args[0] is None:
            return None
        return super().__new__(cls, *args, **kwargs)


class ProjectScheme(BaseScheme):
    render_fields = ['id', 'name', 'user_id']
    properties = {
        "id": typesystem.integer(default=0),
        "name": typesystem.String,
        "user_id": NullableInt
    }


class Project(Base):
    __tablename__ = "projects"
    _scheme = ProjectScheme

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="projects")
