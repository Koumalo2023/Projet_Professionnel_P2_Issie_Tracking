from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    type = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))

    # Relations
    author = relationship("User", back_populates="projects")
    issues = relationship("Issue", back_populates="project")
    contributors = relationship("Contributor", back_populates="project")