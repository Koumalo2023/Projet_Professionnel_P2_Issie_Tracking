from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.database import Base

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(Enum("To Do", "In Progress", "Finished", name="status_enum"))
    priority = Column(Enum("LOW", "MEDIUM", "HIGH", name="priority_enum"))
    tag = Column(Enum("BUG", "FEATURE", "TASK", name="tag_enum"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    author_id = Column(Integer, ForeignKey("users.id"))

    # Relations
    project = relationship("Project", back_populates="issues")
    author = relationship("User", back_populates="issues")
    comments = relationship("Comment", back_populates="issue")