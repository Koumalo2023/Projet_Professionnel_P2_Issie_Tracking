# api/app/repositories/issue_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.issue import Issue
from app.schemas.issue_schema import IssueCreate, IssueUpdate

class IssueRepository:
    def create_issue(self, db: Session, project_id: int, issue: IssueCreate, author_id: int) -> Issue:
        """
        Crée une nouvelle issue pour un projet.
        """
        db_issue = Issue(
            name=issue.name,
            description=issue.description,
            priority=issue.priority,
            tag=issue.tag,
            status="To Do",  # Statut par défaut
            assigned_to=issue.assigned_to,
            project_id=project_id,
            author_id=author_id,
        )
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        return db_issue

    def get_all_issues(self, db: Session, project_id: int, skip: int = 0, limit: int = 10) -> List[Issue]:
        """
        Récupère toutes les issues d'un projet avec pagination.
        """
        return db.query(Issue).filter(Issue.project_id == project_id).offset(skip).limit(limit).all()

    def get_issue_by_id(self, db: Session, project_id: int, issue_id: int) -> Issue:
        """
        Récupère une issue spécifique par son ID.
        """
        return db.query(Issue).filter(Issue.project_id == project_id, Issue.id == issue_id).first()

    def update_issue(self, db: Session, issue_id: int, issue_update: IssueUpdate) -> Issue:
        """
        Met à jour une issue.
        """
        db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not db_issue:
            return None
        for key, value in issue_update.dict(exclude_unset=True).items():
            setattr(db_issue, key, value)
        db.commit()
        db.refresh(db_issue)
        return db_issue

    def delete_issue(self, db: Session, issue_id: int) -> None:
        """
        Supprime une issue.
        """
        db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not db_issue:
            return None
        db.delete(db_issue)
        db.commit()