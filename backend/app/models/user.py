
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer)
    can_be_contacted = Column(Boolean, default=False)
    can_data_be_shared = Column(Boolean, default=False)

    # Relations
    projects = relationship("Project", back_populates="author")
    issues = relationship("Issue", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    contributions = relationship("Contributor", back_populates="user")