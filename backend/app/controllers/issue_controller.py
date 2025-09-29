# api/app/controllers/issue_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.models.issue import Issue
from app.schemas.issue_schema import IssueCreate, IssueResponse, IssueUpdate
from app.services.issue_service import IssueService
from app.repositories.issue_repository import IssueRepository
from app.database.dependencies import get_db
from app.auth.auth_utils import get_current_user
from app.models.user import User
from app.auth.permission_decorators import (
    can_create_issue, can_read_issue, can_update_issue,
    can_delete_issue, project_member_required
)

router = APIRouter(prefix="/issues", tags=["issues"])

@router.post("/projects/{project_id}/issues", response_model=dict)
@can_create_issue("project_id")
def create_issue(
    project_id: int,
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue_repository = IssueRepository()
    issue_service = IssueService(issue_repository)
    db_issue = issue_service.create_issue(project_id, issue, db, current_user.id)
    return {"issue_id": db_issue.id, "message": "Issue created successfully"}

@router.get("/projects/{project_id}/issues", response_model=dict)
@can_read_issue("project_id")
def get_all_issues(
    project_id: int,
    skip: int = Query(0, description="Nombre d'issues à sauter"),
    limit: int = Query(10, description="Nombre d'issues à retourner"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue_repository = IssueRepository()
    issue_service = IssueService(issue_repository)
    issues = issue_service.get_all_issues(project_id, db, skip, limit)
    return {
        "issues": [
            {
                "id": issue.id,
                "name": issue.name,
                "description": issue.description,
                "priority": issue.priority,
                "tag": issue.tag,
                "status": issue.status,
                "assigned_to": issue.assigned_to,
            }
            for issue in issues
        ],
        "page": skip // limit + 1,
        "total_pages": (db.query(Issue).filter(Issue.project_id == project_id).count() + limit - 1) // limit,
    }

@router.get("/projects/{project_id}/issues/{issue_id}", response_model=IssueResponse)
@can_read_issue("project_id")
def get_issue(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue_repository = IssueRepository()
    issue_service = IssueService(issue_repository)
    issue = issue_service.get_issue_by_id(project_id, issue_id, db)
    return issue

@router.put("/projects/{project_id}/issues/{issue_id}", response_model=dict)
@can_update_issue("project_id")
def update_issue(
    project_id: int,
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue_repository = IssueRepository()
    issue_service = IssueService(issue_repository)
    updated_issue = issue_service.update_issue(project_id, issue_id, issue_update, db)
    return {"message": "Issue updated successfully"}

@router.delete("/projects/{project_id}/issues/{issue_id}", response_model=dict)
@can_delete_issue("project_id")
def delete_issue(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue_repository = IssueRepository()
    issue_service = IssueService(issue_repository)
    issue_service.delete_issue(project_id, issue_id, db)
    return {"message": "Issue deleted successfully"}