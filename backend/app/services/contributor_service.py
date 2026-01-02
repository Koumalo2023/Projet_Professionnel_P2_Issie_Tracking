# api/app/services/contributor_service.py
from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.contributor import Contributor
from app.models.user import User
from app.models.project import Project
from app.repositories.contributor_repository import ContributorRepository
from app.database.dependencies import get_db

class ContributorService:
    def __init__(self, contributor_repository: ContributorRepository):
        self.contributor_repository = contributor_repository

    def add_contributor(self, project_id: int, user_id: int, db: Session) -> Contributor:
        """
        Ajoute un contributeur à un projet.
        """
        # Vérifie si l'utilisateur existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Vérifie si le projet existe
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # Vérifie si l'utilisateur est déjà contributeur
        existing_contributor = db.query(Contributor).filter(Contributor.project_id == project_id, Contributor.user_id == user_id).first()
        if existing_contributor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a contributor")

        # Ajoute le contributeur
        db_contributor = self.contributor_repository.add_contributor(db, project_id, user_id)
        return db_contributor

    def get_contributors(self, project_id: int, db: Session) -> List[Contributor]:
        """
        Récupère tous les contributeurs d'un projet.
        """
        contributors = self.contributor_repository.get_contributors(db, project_id)
        return contributors

    def remove_contributor(self, project_id: int, user_id: int, db: Session) -> None:
        """
        Supprime un contributeur d'un projet.
        """
        contributor = db.query(Contributor).filter(Contributor.project_id == project_id, Contributor.user_id == user_id).first()
        if not contributor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contributor not found")
        self.contributor_repository.remove_contributor(db, project_id, user_id)