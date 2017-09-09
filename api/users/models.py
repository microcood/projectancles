from sqlalchemy import Column, Integer, String
from apistar import typesystem
from db_base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)


class UserType(typesystem.Object):
    properties = {
        "id": typesystem.integer(default=0),
        "first_name": typesystem.String,
        "last_name": typesystem.String
    }
