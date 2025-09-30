# backend/app/controllers/token_controller.py
"""
Contrôleur pour la gestion des tokens avec rafraîchissement automatique et rotation sécurisée
Endpoints pour le rafraîchissement, la révocation et la gestion du cycle de vie des tokens
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.database import get_db
from app.services.token_service import TokenService, get_token_service
from app.schemas.token_schema import (
    TokenRefreshRequest,
    TokenResponse,
    TokenRevokeRequest,
    TokenRevokeResponse,
    TokenMetricsResponse,
    TokenCleanupStats,
    TokenValidationResponse
)
from app.exceptions.session_exceptions import (
    TokenExpiredException,
    InvalidTokenException,
    TokenRevokedException
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rafraîchir les tokens",
    description="Rafraîchit les tokens d'accès et de rafraîchissement avec rotation sécurisée"
)
async def refresh_tokens(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Rafraîchit les tokens avec rotation sécurisée
    
    - **refresh_token**: Token de rafraîchissement valide
    - **ip_address**: Adresse IP du client (optionnel)
    - **user_agent**: User-Agent du navigateur (optionnel)
    
    Retourne une nouvelle paire de tokens (access + refresh)
    """
    try:
        # Utilise l'adresse IP de la requête si non fournie
        ip_address = request.ip_address
        user_agent = request.user_agent
        
        # Rafraîchit les tokens
        access_token, refresh_token, session = token_service.refresh_tokens(
            old_refresh_token=request.refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Calcule la durée d'expiration en secondes
        expires_in = token_service.access_token_expire_minutes * 60
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            session_id=session.id
        )
        
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement expiré"
        )
    except InvalidTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenRevokedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement des tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du rafraîchissement des tokens"
        )


@router.post(
    "/revoke",
    response_model=TokenRevokeResponse,
    summary="Révoquer des tokens",
    description="Révoque des tokens spécifiques ou tous les tokens d'un utilisateur"
)
async def revoke_tokens(
    request: TokenRevokeRequest,
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service),
    # Dans une implémentation réelle, vous auriez un système d'authentification
    # current_user: User = Depends(get_current_user)
):
    """
    Révoque des tokens
    
    - **session_id**: ID de session spécifique à révoquer (optionnel)
    - **revoke_all**: Révoquer toutes les sessions de l'utilisateur (défaut: False)
    
    Si revoke_all=True, révoque toutes les sessions de l'utilisateur
    Si session_id est fourni, révoque uniquement cette session
    """
    try:
        # Dans une implémentation réelle, vous obtiendriez l'utilisateur courant
        # user_id = current_user.id
        # Pour cette démo, nous utilisons un ID fixe
        user_id = 1
        
        revoked_count = 0
        
        if request.revoke_all:
            # Révoque toutes les sessions
            revoked_count = token_service.revoke_all_user_tokens(user_id)
            message = f"Toutes les sessions révoquées ({revoked_count} sessions)"
            
        elif request.session_id:
            # Révoque une session spécifique
            success = token_service.revoke_tokens(request.session_id)
            if success:
                revoked_count = 1
                message = f"Session {request.session_id} révoquée"
            else:
                message = f"Session {request.session_id} non trouvée"
                
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Spécifiez soit session_id soit revoke_all=True"
            )
        
        return TokenRevokeResponse(
            message=message,
            revoked_count=revoked_count
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la révocation des tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la révocation des tokens"
        )


@router.get(
    "/metrics",
    response_model=TokenMetricsResponse,
    summary="Métriques des tokens",
    description="Retourne les métriques des tokens pour l'utilisateur courant"
)
async def get_token_metrics(
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service),
    # current_user: User = Depends(get_current_user)
):
    """
    Retourne les métriques des tokens
    
    - **active_sessions**: Nombre de sessions actives
    - **soon_expiring_sessions**: Sessions expirant bientôt
    - **max_allowed_sessions**: Maximum de sessions autorisées
    - **access_token_duration_minutes**: Durée du token d'accès
    - **refresh_token_duration_days**: Durée du token de rafraîchissement
    - **can_create_new_session**: Si une nouvelle session peut être créée
    """
    try:
        # Dans une implémentation réelle, vous obtiendriez l'utilisateur courant
        # user_id = current_user.id
        user_id = 1
        
        metrics = token_service.get_token_metrics(user_id)
        
        # Ajoute si l'utilisateur peut créer une nouvelle session
        metrics["can_create_new_session"] = (
            metrics["active_sessions"] < metrics["max_allowed_sessions"]
        )
        
        return TokenMetricsResponse(**metrics)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des métriques"
        )


@router.post(
    "/cleanup",
    response_model=TokenCleanupStats,
    summary="Nettoyer les tokens expirés",
    description="Nettoie les tokens expirés et révoqués (opération d'administration)"
)
async def cleanup_expired_tokens(
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Nettoie les tokens expirés
    
    Cette opération supprime:
    - Les sessions expirées
    - Les tokens de rafraîchissement expirés
    
    Retourne les statistiques du nettoyage
    """
    try:
        stats = token_service.cleanup_expired_tokens()
        
        logger.info(f"Nettoyage des tokens terminé: {stats}")
        
        return TokenCleanupStats(**stats)
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du nettoyage des tokens"
        )


@router.post(
    "/validate",
    response_model=TokenValidationResponse,
    summary="Valider un token",
    description="Valide un token d'accès et retourne ses informations"
)
async def validate_token(
    token: str,
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Valide un token d'accès
    
    - **token**: Token JWT à valider
    
    Retourne les informations de validation
    """
    try:
        payload = token_service.validate_access_token(token)
        
        # Calcule le temps restant
        from datetime import datetime
        exp_timestamp = payload.get("exp")
        remaining_seconds = None
        
        if exp_timestamp:
            exp_time = datetime.fromtimestamp(exp_timestamp)
            remaining_seconds = int((exp_time - datetime.utcnow()).total_seconds())
            remaining_seconds = max(0, remaining_seconds)  # Évite les valeurs négatives
        
        return TokenValidationResponse(
            is_valid=True,
            user_id=payload.get("user_id"),
            session_id=payload.get("session_id"),
            username=payload.get("username"),
            expires_at=datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None,
            remaining_seconds=remaining_seconds
        )
        
    except TokenExpiredException:
        return TokenValidationResponse(
            is_valid=False,
            remaining_seconds=0
        )
    except InvalidTokenException:
        return TokenValidationResponse(
            is_valid=False
        )
    except Exception as e:
        logger.error(f"Erreur lors de la validation du token: {str(e)}")
        return TokenValidationResponse(
            is_valid=False
        )


@router.get(
    "/config",
    summary="Configuration des tokens",
    description="Retourne la configuration actuelle des tokens"
)
async def get_token_config(
    token_service: TokenService = Depends(get_token_service)
) -> Dict[str, Any]:
    """
    Retourne la configuration des tokens
    
    - **access_token_expire_minutes**: Durée du token d'accès
    - **refresh_token_expire_days**: Durée du token de rafraîchissement
    - **max_refresh_tokens_per_user**: Maximum de tokens par utilisateur
    - **jwt_algorithm**: Algorithme JWT utilisé
    """
    return {
        "access_token_expire_minutes": token_service.access_token_expire_minutes,
        "refresh_token_expire_days": token_service.refresh_token_expire_days,
        "max_refresh_tokens_per_user": token_service.max_refresh_tokens_per_user,
        "jwt_algorithm": token_service.jwt_algorithm,
        "automatic_rotation_enabled": True
    }


# Endpoint de santé pour le service de tokens
@router.get("/health")
async def token_health_check(
    token_service: TokenService = Depends(get_token_service)
) -> Dict[str, str]:
    """
    Vérification de santé du service de tokens
    """
    try:
        # Test simple de fonctionnement
        test_token = "test"
        try:
            token_service.validate_access_token(test_token)
        except (InvalidTokenException, TokenExpiredException):
            # C'est normal pour un token de test invalide
            pass
        
        return {"status": "healthy", "service": "token_service"}
        
    except Exception as e:
        logger.error(f"Erreur de santé du service de tokens: {str(e)}")
        return {"status": "unhealthy", "service": "token_service", "error": str(e)}