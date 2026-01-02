# api/app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.auth_schema import Token
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.database.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_repository = UserRepository()
    auth_service = AuthService(user_repository)
    user = auth_service.authenticate_user(form_data.username, form_data.password, db)
    tokens = auth_service.create_tokens(user)
    return tokens

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    user_repository = UserRepository()
    auth_service = AuthService(user_repository)
    tokens = auth_service.refresh_access_token(refresh_token)
    return tokens