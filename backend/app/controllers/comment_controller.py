# api/app/controllers/comment_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.models.comment import Comment
from app.schemas.comment_schema import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment_service import CommentService
from app.repositories.comment_repository import CommentRepository
from app.database.dependencies import get_db
from app.auth.auth_utils import get_current_user
from app.models.user import User

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/projects/{project_id}/issues/{issue_id}/comments", response_model=dict)
def create_comment(
    project_id: int,
    issue_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment_repository = CommentRepository()
    comment_service = CommentService(comment_repository)
    db_comment = comment_service.create_comment(issue_id, comment, db, current_user.id)
    return {"comment_id": db_comment.id, "message": "Comment added successfully"}

@router.get("/projects/{project_id}/issues/{issue_id}/comments", response_model=dict)
def get_all_comments(
    project_id: int,
    issue_id: int,
    skip: int = Query(0, description="Nombre de commentaires à sauter"),
    limit: int = Query(10, description="Nombre de commentaires à retourner"),
    db: Session = Depends(get_db),
):
    comment_repository = CommentRepository()
    comment_service = CommentService(comment_repository)
    comments = comment_service.get_all_comments(issue_id, db, skip, limit)
    return {
        "comments": [
            {"id": comment.id, "description": comment.description, "author": comment.author_id}
            for comment in comments
        ],
        "page": skip // limit + 1,
        "total_pages": (db.query(Comment).filter(Comment.issue_id == issue_id).count() + limit - 1) // limit,
    }

@router.get("/projects/{project_id}/issues/{issue_id}/comments/{comment_id}", response_model=CommentResponse)
def get_comment(
    project_id: int,
    issue_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
):
    comment_repository = CommentRepository()
    comment_service = CommentService(comment_repository)
    comment = comment_service.get_comment_by_id(issue_id, comment_id, db)
    return comment

@router.put("/projects/{project_id}/issues/{issue_id}/comments/{comment_id}", response_model=dict)
def update_comment(
    project_id: int,
    issue_id: int,
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment_repository = CommentRepository()
    comment_service = CommentService(comment_repository)
    updated_comment = comment_service.update_comment(issue_id, comment_id, comment_update, db)
    return {"message": "Comment updated successfully"}

@router.delete("/projects/{project_id}/issues/{issue_id}/comments/{comment_id}", response_model=dict)
def delete_comment(
    project_id: int,
    issue_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment_repository = CommentRepository()
    comment_service = CommentService(comment_repository)
    comment_service.delete_comment(issue_id, comment_id, db)
    return {"message": "Comment deleted successfully"}