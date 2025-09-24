# api/app/services/comment_service.py
from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.user import User
from app.database.dependencies import get_db
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment_schema import CommentCreate, CommentUpdate

class CommentService:
    def __init__(self, comment_repository: CommentRepository):
        self.comment_repository = comment_repository

    def create_comment(self, issue_id: int, comment: CommentCreate, db: Session, author_id: int) -> Comment:
        """
        Ajoute un commentaire à une issue.
        """
        # Vérifie si l'issue existe
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

        # Crée le commentaire
        db_comment = self.comment_repository.create_comment(db, issue_id, comment, author_id)
        return db_comment

    def get_all_comments(self, issue_id: int, db: Session, skip: int = 0, limit: int = 10) -> List[Comment]:
        """
        Récupère tous les commentaires d'une issue avec pagination.
        """
        return self.comment_repository.get_all_comments(db, issue_id, skip, limit)

    def get_comment_by_id(self, issue_id: int, comment_id: int, db: Session) -> Comment:
        """
        Récupère un commentaire spécifique par son ID.
        """
        comment = self.comment_repository.get_comment_by_id(db, issue_id, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        return comment

    def update_comment(self, issue_id: int, comment_id: int, comment_update: CommentUpdate, db: Session) -> Comment:
        """
        Met à jour un commentaire.
        """
        comment = self.comment_repository.get_comment_by_id(db, issue_id, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        updated_comment = self.comment_repository.update_comment(db, comment_id, comment_update)
        return updated_comment

    def delete_comment(self, issue_id: int, comment_id: int, db: Session) -> None:
        """
        Supprime un commentaire.
        """
        comment = self.comment_repository.get_comment_by_id(db, issue_id, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        self.comment_repository.delete_comment(db, comment_id)