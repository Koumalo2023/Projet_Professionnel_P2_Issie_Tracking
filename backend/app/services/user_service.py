# api/app/services/user_service.py
from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.auth.auth_utils import get_password_hash, verify_password
from app.database.dependencies import get_db
from app.schemas.user_schema import UserCreate, UserUpdate

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user: UserCreate, db: Session) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = self.user_repository.create_user(
            db,
            username=user.username,
            email=user.email,
            age=user.age,
            hashed_password=hashed_password,
            can_be_contacted=user.can_be_contacted,
            can_data_be_shared=user.can_data_be_shared,
        )
        return db_user


    def get_all_users(self, db: Session, skip: int = 0, limit: int = 10) -> List[User]:
        """
        Récupère tous les utilisateurs avec pagination.
        """
        return self.user_repository.get_all_users(db, skip, limit)

    def get_user_by_id(self, user_id: int, db: Session) -> User:
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user


    def get_user_by_username(self, db: Session, username: str) -> User:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        """
        return self.user_repository.get_user_by_username(db, username)

    def update_user(self, user_id: int, user_update: UserUpdate, db: Session) -> User:
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        updated_user = self.user_repository.update_user(db, user_id, user_update)
        return updated_user

    def delete_user(self, user_id: int, db: Session) -> None:
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.user_repository.delete_user(db, user_id)