# api/app/services/issue_service.py
from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.issue import Issue
from app.models.project import Project
from app.models.user import User
from app.repositories.issue_repository import IssueRepository
from app.database.dependencies import get_db
from app.schemas.issue_schema import IssueCreate, IssueUpdate

class IssueService:
    def __init__(self, issue_repository: IssueRepository):
        self.issue_repository = issue_repository

    def create_issue(self, project_id: int, issue: IssueCreate, db: Session, user_id: int) -> Issue:
        """
        Crée une nouvelle issue pour un projet.
        """
        # Vérifie si le projet existe
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # Vérifie si l'utilisateur assigné existe
        assigned_user = db.query(User).filter(User.id == issue.assigned_to).first()
        if not assigned_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

        # Crée l'issue
        db_issue = self.issue_repository.create_issue(db, project_id, issue, user_id)
        return db_issue

    def get_all_issues(self, project_id: int, db: Session, skip: int = 0, limit: int = 10) -> List[Issue]:
        """
        Récupère toutes les issues d'un projet avec pagination.
        """
        return self.issue_repository.get_all_issues(db, project_id, skip, limit)

    def get_issue_by_id(self, project_id: int, issue_id: int, db: Session) -> Issue:
        """
        Récupère une issue spécifique par son ID.
        """
        issue = self.issue_repository.get_issue_by_id(db, project_id, issue_id)
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return issue

    def update_issue(self, project_id: int, issue_id: int, issue_update: IssueUpdate, db: Session) -> Issue:
        """
        Met à jour une issue.
        """
        issue = self.issue_repository.get_issue_by_id(db, project_id, issue_id)
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        updated_issue = self.issue_repository.update_issue(db, issue_id, issue_update)
        return updated_issue

    def delete_issue(self, project_id: int, issue_id: int, db: Session) -> None:
        """
        Supprime une issue.
        """
        issue = self.issue_repository.get_issue_by_id(db, project_id, issue_id)
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        self.issue_repository.delete_issue(db, issue_id)