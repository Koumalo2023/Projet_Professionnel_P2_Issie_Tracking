from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Contributor(Base):
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    # Relations
    user = relationship("User", back_populates="contributions")
    project = relationship("Project", back_populates="contributors")