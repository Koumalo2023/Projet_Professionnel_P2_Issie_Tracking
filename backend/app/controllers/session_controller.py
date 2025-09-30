# backend/app/controllers/session_controller.py
"""
Contrôleur pour la gestion des sessions utilisateur
API pour le suivi des connexions actives et historique des sessions
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.session_service import SessionService, get_session_service
from app.auth.auth_utils import get_current_user
from app.models.user import User
from app.models.session import UserSession, LoginHistory, SecurityEvent
from app.schemas.session_schema import (
    SessionResponse,
    ActiveSessionsResponse,
    LoginHistoryResponse,
    SecurityEventsResponse,
    SessionInfo,
    LoginHistoryInfo,
    SecurityEventInfo
)
from app.exceptions.session_exceptions import (
    SessionNotFoundException,
    SessionExpiredException,
    TooManyActiveSessionsException,
    InvalidSessionException
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/active", response_model=ActiveSessionsResponse)
async def get_active_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Récupère toutes les sessions actives de l'utilisateur connecté
    """
    try:
        active_sessions = session_service.get_active_sessions(current_user)
        
        sessions_info = []
        for session in active_sessions:
            sessions_info.append(SessionInfo(
                id=session.id,
                ip_address=session.ip_address,
                device_type=session.device_type,
                browser=session.browser,
                platform=session.platform,
                created_at=session.created_at,
                last_activity=session.last_activity,
                expires_at=session.expires_at,
                is_mobile=session.is_mobile
            ))
        
        return ActiveSessionsResponse(
            sessions=sessions_info,
            total_active=len(sessions_info)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sessions actives: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des sessions actives"
        )


@router.delete("/{session_id}", response_model=SessionResponse)
async def logout_session(
    session_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Déconnecte une session spécifique
    """
    try:
        # Récupère la session
        session = request.app.state.db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise SessionNotFoundException()
        
        # Déconnecte la session
        success = session_service.logout_session(
            session_token=session.session_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        if success:
            return SessionResponse(
                message="Session déconnectée avec succès",
                session_id=session_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la déconnexion de la session"
            )
            
    except SessionNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session non trouvée"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion de la session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la déconnexion de la session"
        )


@router.post("/logout-all", response_model=SessionResponse)
async def logout_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Déconnecte toutes les sessions de l'utilisateur connecté
    """
    try:
        success = session_service.logout_all_sessions(
            user=current_user,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        if success:
            return SessionResponse(
                message="Toutes les sessions ont été déconnectées avec succès"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la déconnexion de toutes les sessions"
            )
            
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion de toutes les sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la déconnexion de toutes les sessions"
        )


@router.get("/history", response_model=LoginHistoryResponse)
async def get_login_history(
    request: Request,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Récupère l'historique des connexions de l'utilisateur
    """
    try:
        history = session_service.get_session_history(current_user, limit)
        
        history_info = []
        for entry in history:
            history_info.append(LoginHistoryInfo(
                id=entry.id,
                login_type=entry.login_type,
                provider=entry.provider,
                ip_address=entry.ip_address,
                location=entry.location,
                success=entry.success,
                failure_reason=entry.failure_reason,
                login_at=entry.login_at,
                logout_at=entry.logout_at,
                duration_seconds=entry.get_duration().total_seconds() if entry.logout_at else None
            ))
        
        return LoginHistoryResponse(
            history=history_info,
            total_entries=len(history_info)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'historique des connexions"
        )


@router.get("/security-events", response_model=SecurityEventsResponse)
async def get_security_events(
    request: Request,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Récupère les événements de sécurité de l'utilisateur
    """
    try:
        events = session_service.get_security_events(current_user, limit)
        
        events_info = []
        for event in events:
            events_info.append(SecurityEventInfo(
                id=event.id,
                event_type=event.event_type,
                severity=event.severity,
                description=event.description,
                ip_address=event.ip_address,
                created_at=event.created_at
            ))
        
        return SecurityEventsResponse(
            events=events_info,
            total_events=len(events_info)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des événements de sécurité: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des événements de sécurité"
        )


@router.post("/refresh", response_model=SessionResponse)
async def refresh_session(
    request: Request,
    refresh_token: str,
    session_service: SessionService = Depends(get_session_service)
):
    """
    Rafraîchit une session avec un token de rafraîchissement
    """
    try:
        session = session_service.refresh_session(
            refresh_token=refresh_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        return SessionResponse(
            message="Session rafraîchie avec succès",
            session_id=session.id
        )
        
    except SessionNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session non trouvée"
        )
    except SessionExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée"
        )
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement de la session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du rafraîchissement de la session"
        )


@router.post("/cleanup")
async def cleanup_expired_sessions(
    session_service: SessionService = Depends(get_session_service)
):
    """
    Nettoie les sessions expirées (endpoint admin)
    """
    try:
        cleaned_count = session_service.cleanup_expired_sessions()
        
        return {
            "message": f"{cleaned_count} sessions expirées nettoyées",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du nettoyage des sessions expirées"
        )


@router.get("/current", response_model=SessionInfo)
async def get_current_session_info(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Récupère les informations de la session actuelle
    """
    try:
        # Cette fonctionnalité nécessiterait de stocker l'ID de session dans le JWT
        # Pour l'instant, nous retournons une réponse simplifiée
        
        return SessionInfo(
            ip_address=request.client.host,
            device_type="web",  # À détecter à partir du User-Agent
            browser="Unknown",
            platform="Unknown",
            created_at=None,
            last_activity=None,
            expires_at=None,
            is_mobile=False
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des informations de session"
        )


# Middleware pour mettre à jour l'activité de session
async def update_session_activity_middleware(request: Request, call_next):
    """
    Middleware pour mettre à jour l'activité de session à chaque requête
    """
    response = await call_next(request)
    
    # Met à jour l'activité de session si l'utilisateur est authentifié
    if hasattr(request.state, "user") and request.state.user:
        try:
            session_service = get_session_service(request.app.state.db)
            
            # Récupère le token de session depuis l'en-tête Authorization
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                session_token = auth_header.replace("Bearer ", "")
                
                # Valide et met à jour la session
                session_service.validate_session(
                    session_token=session_token,
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent")
                )
        except (SessionNotFoundException, SessionExpiredException, InvalidSessionException):
            # Si la session est invalide, on ne fait rien - l'authentification échouera
            pass
        except Exception as e:
            # On log l'erreur mais on ne bloque pas la requête
            logger.warning(f"Erreur lors de la mise à jour de l'activité de session: {str(e)}")
    
    return response