# api/app/controllers/contributor_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.contributor_schema import ContributorCreate, ContributorResponse
from app.services.contributor_service import ContributorService
from app.repositories.contributor_repository import ContributorRepository
from app.database.dependencies import get_db
from app.auth.auth_utils import get_current_user
from app.models.user import User

router = APIRouter(prefix="/contributors", tags=["contributors"])

@router.post("/projects/{project_id}/contributors", response_model=dict)
def add_contributor(
    project_id: int,
    contributor: ContributorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contributor_repository = ContributorRepository()
    contributor_service = ContributorService(contributor_repository)
    contributor_service.add_contributor(project_id, contributor.user_id, db)
    return {"message": "Contributor added successfully"}

@router.get("/projects/{project_id}/contributors", response_model=dict)
def get_contributors(
    project_id: int,
    db: Session = Depends(get_db),
):
    contributor_repository = ContributorRepository()
    contributor_service = ContributorService(contributor_repository)
    contributors = contributor_service.get_contributors(project_id, db)
    return {
        "contributors": [
            {"user_id": contributor.user_id, "username": contributor.user.username}
            for contributor in contributors
        ]
    }

@router.delete("/projects/{project_id}/contributors/{user_id}", response_model=dict)
def remove_contributor(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contributor_repository = ContributorRepository()
    contributor_service = ContributorService(contributor_repository)
    contributor_service.remove_contributor(project_id, user_id, db)
    return {"message": "Contributor removed successfully"}