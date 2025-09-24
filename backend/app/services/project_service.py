# api/app/services/project_service.py
from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.database.dependencies import get_db
from app.schemas.project_schema import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    def create_project(self, project: ProjectCreate, db: Session, user_id: int) -> Project:
        """
        Crée un nouveau projet.
        """
        db_project = self.project_repository.create_project(db, project, user_id)
        return db_project

    def get_all_projects(self, db: Session, skip: int = 0, limit: int = 10) -> List[Project]:
        """
        Récupère tous les projets avec pagination.
        """
        return self.project_repository.get_all_projects(db, skip, limit)

    def get_project_by_id(self, db: Session, project_id: int) -> Project:
        """
        Récupère un projet par son ID.
        """
        project = self.project_repository.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    def update_project(self, db: Session, project_id: int, project_update: ProjectUpdate) -> Project:
        """
        Met à jour un projet.
        """
        project = self.project_repository.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        updated_project = self.project_repository.update_project(db, project_id, project_update)
        return updated_project

    def delete_project(self, db: Session, project_id: int) -> None:
        """
        Supprime un projet.
        """
        project = self.project_repository.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        self.project_repository.delete_project(db, project_id)