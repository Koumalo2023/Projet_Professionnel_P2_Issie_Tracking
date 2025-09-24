# api/app/repositories/project_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate

class ProjectRepository:
    def create_project(self, db: Session, project: ProjectCreate, user_id: int) -> Project:
        """
        Crée un nouveau projet.
        """
        db_project = Project(
            name=project.name,
            description=project.description,
            type=project.type,
            author_id=user_id,
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    def get_all_projects(self, db: Session, skip: int = 0, limit: int = 10) -> List[Project]:
        """
        Récupère tous les projets avec pagination.
        """
        return db.query(Project).offset(skip).limit(limit).all()

    def get_project_by_id(self, db: Session, project_id: int) -> Project:
        """
        Récupère un projet par son ID.
        """
        return db.query(Project).filter(Project.id == project_id).first()

    def update_project(self, db: Session, project_id: int, project_update: ProjectUpdate) -> Project:
        """
        Met à jour un projet.
        """
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return None
        for key, value in project_update.dict(exclude_unset=True).items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
        return db_project

    def delete_project(self, db: Session, project_id: int) -> None:
        """
        Supprime un projet.
        """
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return None
        db.delete(db_project)
        db.commit()