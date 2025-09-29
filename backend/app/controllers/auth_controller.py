# api/app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.auth_schema import Token
from app.schemas.response_schemas import SuccessResponse, Metadata
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.database.dependencies import get_db
from app.exceptions.business_exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException
)
from app.utils.logger import log_business_event
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=SuccessResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authentifie un utilisateur et retourne des tokens JWT
    """
    try:
        user_repository = UserRepository()
        auth_service = AuthService(user_repository)
        
        # Authentification de l'utilisateur
        user = auth_service.authenticate_user(form_data.username, form_data.password, db)
        
        # Création des tokens
        tokens = auth_service.create_tokens(user)
        
        # Log de l'événement métier
        log_business_event(
            event_type="USER_LOGIN_SUCCESS",
            message=f"User {user.username} logged in successfully",
            user_id=user.id
        )
        
        # Réponse standardisée
        return SuccessResponse(
            data=tokens,
            metadata=Metadata(timestamp=datetime.utcnow())
        )
        
    except InvalidCredentialsException:
        # Log de l'échec de connexion
        log_business_event(
            event_type="USER_LOGIN_FAILED",
            message=f"Failed login attempt for username: {form_data.username}",
            extra_data={"reason": "invalid_credentials"}
        )
        raise
    except Exception as e:
        # Log des erreurs inattendues
        log_business_event(
            event_type="USER_LOGIN_ERROR",
            message=f"Unexpected error during login for username: {form_data.username}",
            extra_data={"error": str(e)}
        )
        raise

@router.post("/refresh", response_model=SuccessResponse)
def refresh_token(refresh_token: str):
    """
    Rafraîchit un token d'accès à partir d'un refresh token
    """
    try:
        user_repository = UserRepository()
        auth_service = AuthService(user_repository)
        
        # Rafraîchissement du token
        tokens = auth_service.refresh_access_token(refresh_token)
        
        # Log de l'événement métier
        log_business_event(
            event_type="TOKEN_REFRESH_SUCCESS",
            message="Token refreshed successfully"
        )
        
        # Réponse standardisée
        return SuccessResponse(
            data=tokens,
            metadata=Metadata(timestamp=datetime.utcnow())
        )
        
    except (InvalidTokenException, TokenExpiredException):
        # Log de l'échec de rafraîchissement
        log_business_event(
            event_type="TOKEN_REFRESH_FAILED",
            message="Token refresh failed",
            extra_data={"reason": "invalid_or_expired_token"}
        )
        raise
    except Exception as e:
        # Log des erreurs inattendues
        log_business_event(
            event_type="TOKEN_REFRESH_ERROR",
            message="Unexpected error during token refresh",
            extra_data={"error": str(e)}
        )
        raise

@router.post("/logout")
def logout():
    """
    Déconnecte un utilisateur (invalide le token côté client)
    """
    # Note: Dans une implémentation JWT stateless, la déconnexion est gérée côté client
    # en supprimant le token. Cette endpoint est principalement pour la documentation.
    
    log_business_event(
        event_type="USER_LOGOUT",
        message="User logged out"
    )
    
    return SuccessResponse(
        data={"message": "Logout successful"},
        metadata=Metadata(timestamp=datetime.utcnow())
    )