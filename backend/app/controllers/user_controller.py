# api/app/controllers/user_controller.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.database.dependencies import get_db
from app.auth.auth_utils import create_access_token, verify_password, get_current_user
from app.models.user import User
from app.auth.permission_decorators import admin_required

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=dict)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    db_user = user_service.create_user(user, db)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"token": access_token}

@router.post("/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    db_user = user_service.get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"token": access_token}


@router.get("/users", response_model=List[UserResponse])
@admin_required
def get_all_users(
    skip: int = Query(0, description="Nombre d'utilisateurs à sauter"),
    limit: int = Query(10, description="Nombre d'utilisateurs à retourner"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    users = user_service.get_all_users(db, skip, limit)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
@admin_required
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    db_user = user_service.get_user_by_id(user_id, db)
    return db_user

@router.put("/users/{user_id}", response_model=dict)
@admin_required
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    updated_user = user_service.update_user(user_id, user_update, db)
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}", response_model=dict)
@admin_required
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_repository = UserRepository()
    user_service = UserService(user_repository)
    user_service.delete_user(user_id, db)
    return {"message": "User deleted successfully"}