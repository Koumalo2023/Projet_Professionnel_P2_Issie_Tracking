# api/app/controllers/project_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService
from app.repositories.project_repository import ProjectRepository
from app.database.dependencies import get_db
from app.auth.auth_utils import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/projects", response_model=dict)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_repository = ProjectRepository()
    project_service = ProjectService(project_repository)
    db_project = project_service.create_project(project, db, current_user.id)
    return {"project_id": db_project.id, "message": "Project created successfully"}

@router.get("/projects", response_model=dict)
def get_all_projects(
    skip: int = Query(0, description="Nombre de projets à sauter"),
    limit: int = Query(10, description="Nombre de projets à retourner"),
    db: Session = Depends(get_db),
):
    project_repository = ProjectRepository()
    project_service = ProjectService(project_repository)
    projects = project_service.get_all_projects(db, skip, limit)
    return {
        "projects": [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "type": project.type,
            }
            for project in projects
        ],
        "page": skip // limit + 1,
        "total_pages": (db.query(Project).count() + limit - 1) // limit,
    }

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project_repository = ProjectRepository()
    project_service = ProjectService(project_repository)
    project = project_service.get_project_by_id(db, project_id)
    return project

@router.put("/projects/{project_id}", response_model=dict)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_repository = ProjectRepository()
    project_service = ProjectService(project_repository)
    updated_project = project_service.update_project(db, project_id, project_update)
    return {"message": "Project updated successfully"}

@router.delete("/projects/{project_id}", response_model=dict)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_repository = ProjectRepository()
    project_service = ProjectService(project_repository)
    project_service.delete_project(db, project_id)
    return {"message": "Project deleted successfully"}