# api/app/repositories/comment_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.schemas.comment_schema import CommentCreate, CommentUpdate

class CommentRepository:
    def create_comment(self, db: Session, issue_id: int, comment: CommentCreate, author_id: int) -> Comment:
        """
        Crée un nouveau commentaire pour une issue.
        """
        db_comment = Comment(
            description=comment.description,
            issue_id=issue_id,
            author_id=author_id,
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def get_all_comments(self, db: Session, issue_id: int, skip: int = 0, limit: int = 10) -> List[Comment]:
        """
        Récupère tous les commentaires d'une issue avec pagination.
        """
        return db.query(Comment).filter(Comment.issue_id == issue_id).offset(skip).limit(limit).all()

    def get_comment_by_id(self, db: Session, issue_id: int, comment_id: int) -> Comment:
        """
        Récupère un commentaire spécifique par son ID.
        """
        return db.query(Comment).filter(Comment.issue_id == issue_id, Comment.id == comment_id).first()

    def update_comment(self, db: Session, comment_id: int, comment_update: CommentUpdate) -> Comment:
        """
        Met à jour un commentaire.
        """
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            return None
        for key, value in comment_update.dict(exclude_unset=True).items():
            setattr(db_comment, key, value)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def delete_comment(self, db: Session, comment_id: int) -> None:
        """
        Supprime un commentaire.
        """
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            return None
        db.delete(db_comment)
        db.commit()