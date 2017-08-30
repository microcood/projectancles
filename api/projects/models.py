from sqlalchemy import Column, Integer, String
from db_base import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
