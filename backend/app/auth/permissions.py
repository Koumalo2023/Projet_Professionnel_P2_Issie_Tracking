# api/app/auth/permissions.py
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import Project
from app.database.dependencies import get_db
from app.auth.auth_utils import get_current_user

def is_project_contributor(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    """
    Vérifie si l'utilisateur est un contributeur du projet.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.id not in [contributor.user_id for contributor in project.contributors]:
        raise HTTPException(status_code=403, detail="You are not a contributor to this project")
    return user