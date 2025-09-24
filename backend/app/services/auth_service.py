# api/app/services/auth_service.py
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.auth.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.database.dependencies import get_db

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str, db: Session) -> User:
        """
        Authentifie un utilisateur et retourne l'utilisateur si les informations sont valides.
        """
        user = self.user_repository.get_user_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        return user

    def create_tokens(self, user: User) -> dict:
        """
        Crée un token d'accès et un refresh token pour un utilisateur.
        """
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Génère un nouveau token d'accès à partir d'un refresh token.
        """
        payload = decode_token(refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}