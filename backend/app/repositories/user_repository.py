# api/app/repositories/user_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserUpdate

class UserRepository:
    def create_user(self, db: Session, username: str, email: str, age: int, hashed_password: str, can_be_contacted: bool, can_data_be_shared: bool) -> User:
        db_user = User(
            username=username,
            email=email,
            age=age,
            hashed_password=hashed_password,
            can_be_contacted=can_be_contacted,
            can_data_be_shared=can_data_be_shared,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    

    def get_all_users(self, db: Session, skip: int = 0, limit: int = 10) -> List[User]:
        """
        Récupère tous les utilisateurs avec pagination.
        """
        return db.query(User).offset(skip).limit(limit).all()

    def get_user_by_username(self, db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> User:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user(self, db: Session, user_id: int) -> None:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        db.delete(db_user)
        db.commit()