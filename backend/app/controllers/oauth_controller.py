# app/controllers/oauth_controller.py
"""
Contrôleur pour l'authentification OAuth2
Endpoints pour les connexions via Google, GitHub, Microsoft
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.services.oauth_service import OAuthService, get_oauth_service
from app.auth.auth_utils import get_current_user, create_access_token
from app.models.user import User
from app.schemas.oauth_schema import (
    OAuthLoginRequest,
    OAuthLoginResponse,
    OAuthCallbackRequest,
    OAuthLoginResult,
    OAuthTokenResponse,
    OAuthAccountResponse,
    OAuthLinkRequest,
    OAuthUnlinkRequest,
    OAuthRegistrationRequest,
    OAuthStatsResponse,
    OAuthProviderResponse,
    OAuthProviderListResponse,
    OAuthSuccessResponse,
    OAuthUserInfo
)
from app.exceptions.oauth_exceptions import (
    OAuthProviderNotConfiguredException,
    OAuthStateNotFoundException,
    OAuthStateExpiredException,
    OAuthInvalidCodeException,
    OAuthUserNotFoundException,
    OAuthProviderException,
    OAuthRegistrationRequiredException
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/oauth", tags=["OAuth2"])


@router.get("/providers", response_model=OAuthProviderListResponse)
async def get_oauth_providers(
    db: Session = Depends(get_db),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Récupère la liste des providers OAuth2 disponibles
    """
    try:
        # En production, cela viendrait de la base de données
        providers = [
            OAuthProviderResponse(
                id=1,
                name="google",
                display_name="Google",
                authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
                is_enabled=True
            ),
            OAuthProviderResponse(
                id=2,
                name="github",
                display_name="GitHub",
                authorization_url="https://github.com/login/oauth/authorize",
                is_enabled=True
            ),
            OAuthProviderResponse(
                id=3,
                name="microsoft",
                display_name="Microsoft",
                authorization_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                is_enabled=True
            )
        ]
        
        enabled_count = sum(1 for p in providers if p.is_enabled)
        
        return OAuthProviderListResponse(
            providers=providers,
            enabled_count=enabled_count
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des providers OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des providers OAuth2"
        )


@router.post("/login", response_model=OAuthLoginResponse)
async def oauth_login(
    request: OAuthLoginRequest,
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Initie une connexion OAuth2 avec le provider spécifié
    
    Retourne l'URL d'autorisation et le state pour la sécurité CSRF
    """
    try:
        # URI de redirection par défaut (à adapter selon votre frontend)
        redirect_uri = request.redirect_uri or "http://localhost:3000/oauth/callback"
        
        authorization_url, state = oauth_service.get_authorization_url(
            provider=request.provider,
            redirect_uri=redirect_uri
        )
        
        return OAuthLoginResponse(
            authorization_url=authorization_url,
            state=state
        )
    
    except OAuthProviderNotConfiguredException as e:
        logger.warning(f"Tentative de connexion avec provider non configuré: {request.provider}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail)
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de l'initiation OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'initiation de la connexion OAuth2"
        )


@router.post("/callback", response_model=OAuthLoginResult)
async def oauth_callback(
    request: Request,
    callback_request: OAuthCallbackRequest,
    db: Session = Depends(get_db),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Callback OAuth2 après authentification chez le provider
    
    Traite le code d'autorisation et connecte l'utilisateur
    """
    try:
        # Récupère l'IP et l'user agent pour le logging
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent")
        
        # URI de redirection (devrait correspondre à celle utilisée dans /login)
        redirect_uri = "http://localhost:3000/oauth/callback"
        
        # Vérifie le state pour la sécurité CSRF
        oauth_service.verify_state(callback_request.state, "google")  # Provider temporaire
        
        # Échange le code contre un token d'accès
        token_data = oauth_service.exchange_code_for_token(
            provider="google",  # Provider temporaire
            code=callback_request.code,
            redirect_uri=redirect_uri
        )
        
        # Récupère les informations utilisateur
        user_info = oauth_service.get_user_info(
            provider="google",  # Provider temporaire
            access_token=token_data["access_token"]
        )
        
        # Journalise la tentative
        oauth_service.log_oauth_attempt(
            provider="google",
            provider_user_id=user_info["provider_user_id"],
            email=user_info["email"],
            ip_address=client_host,
            user_agent=user_agent,
            success=True
        )
        
        # Trouve ou crée l'utilisateur
        user = oauth_service.find_or_create_user(user_info)
        
        # Crée le token JWT
        access_token = create_access_token(data={"sub": user.username})
        
        return OAuthLoginResult(
            success=True,
            requires_registration=False,
            user_id=user.id,
            access_token=access_token,
            oauth_user_info=OAuthUserInfo(**user_info),
            message="Connexion OAuth2 réussie"
        )
    
    except (OAuthStateNotFoundException, OAuthStateExpiredException) as e:
        logger.warning(f"State OAuth2 invalide: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session de connexion invalide ou expirée"
        )
    
    except OAuthInvalidCodeException as e:
        logger.warning(f"Code OAuth2 invalide: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code d'autorisation invalide"
        )
    
    except OAuthProviderException as e:
        logger.error(f"Erreur provider OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erreur de communication avec le provider OAuth2"
        )
    
    except Exception as e:
        logger.error(f"Erreur lors du callback OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du traitement du callback OAuth2"
        )


@router.post("/link", response_model=OAuthSuccessResponse)
async def link_oauth_account(
    request: OAuthLinkRequest,
    current_user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Lie un compte OAuth2 à un utilisateur connecté
    """
    try:
        # Vérifie le state
        oauth_service.verify_state(request.state, request.provider)
        
        # Échange le code contre un token
        token_data = oauth_service.exchange_code_for_token(
            provider=request.provider,
            code=request.code,
            redirect_uri="http://localhost:3000/oauth/link-callback"
        )
        
        # Récupère les informations utilisateur
        user_info = oauth_service.get_user_info(
            provider=request.provider,
            access_token=token_data["access_token"]
        )
        
        # Lie le compte OAuth2
        oauth_service.link_oauth_account(current_user, user_info)
        
        return OAuthSuccessResponse(
            success=True,
            message=f"Compte {request.provider} lié avec succès"
        )
    
    except OAuthProviderException as e:
        logger.warning(f"Erreur lors de la liaison OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail)
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la liaison OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la liaison du compte OAuth2"
        )


@router.post("/unlink", response_model=OAuthSuccessResponse)
async def unlink_oauth_account(
    request: OAuthUnlinkRequest,
    current_user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Dissocie un compte OAuth2 d'un utilisateur connecté
    """
    try:
        oauth_service.unlink_oauth_account(current_user, request.provider)
        
        return OAuthSuccessResponse(
            success=True,
            message=f"Compte {request.provider} dissocié avec succès"
        )
    
    except OAuthUserNotFoundException as e:
        logger.warning(f"Tentative de dissociation d'un compte OAuth2 inexistant: {request.provider}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte OAuth2 trouvé pour ce provider"
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la dissociation OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la dissociation du compte OAuth2"
        )


@router.get("/accounts", response_model=List[OAuthAccountResponse])
async def get_oauth_accounts(
    current_user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Récupère tous les comptes OAuth2 liés à l'utilisateur connecté
    """
    try:
        oauth_accounts = oauth_service.get_user_oauth_accounts(current_user)
        
        return [
            OAuthAccountResponse(
                id=account.id,
                provider=account.provider.name,
                provider_user_id=account.provider_user_id,
                email=account.email,
                is_primary=account.is_primary,
                created_at=account.created_at,
                last_used=account.updated_at
            )
            for account in oauth_accounts
        ]
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des comptes OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des comptes OAuth2"
        )


@router.post("/register", response_model=OAuthTokenResponse)
async def oauth_register(
    request: OAuthRegistrationRequest,
    db: Session = Depends(get_db),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Finalise l'inscription d'un nouvel utilisateur via OAuth2
    """
    try:
        # Vérifie le state
        oauth_service.verify_state(request.state, request.provider)
        
        # En production, il faudrait vérifier que l'email correspond à celui du provider
        # et créer l'utilisateur avec les informations fournies
        
        # Pour l'instant, nous simulons la création d'utilisateur
        from app.auth.auth_utils import get_password_hash
        
        # Vérifie si l'utilisateur existe déjà
        existing_user = db.query(User).filter(
            (User.username == request.username) | (User.email == request.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec ce nom d'utilisateur ou email existe déjà"
            )
        
        # Crée le nouvel utilisateur
        user = User(
            username=request.username,
            email=request.email,
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            is_active=True,
            email_verified=True  # Les emails OAuth2 sont généralement vérifiés
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Crée le token JWT
        access_token = create_access_token(data={"sub": user.username})
        
        return OAuthTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600  # 1 heure
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'inscription OAuth2"
        )


@router.get("/stats", response_model=OAuthStatsResponse)
async def get_oauth_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques OAuth2 (accessible aux administrateurs uniquement)
    """
    try:
        from app.models.oauth import OAuthUser, OAuthProvider
        from app.models.user import User
        from datetime import datetime, timedelta
        
        # Vérifier les permissions d'administrateur
        # TODO: Implémenter la vérification des permissions administrateur
        
        # Statistiques de base
        total_oauth_users = db.query(OAuthUser).count()
        google_users = db.query(OAuthUser).filter(
            OAuthUser.provider.has(name="google")
        ).count()
        github_users = db.query(OAuthUser).filter(
            OAuthUser.provider.has(name="github")
        ).count()
        microsoft_users = db.query(OAuthUser).filter(
            OAuthUser.provider.has(name="microsoft")
        ).count()
        
        # Calcul du taux d'inscription
        total_users = db.query(User).count()
        oauth_registration_rate = (total_oauth_users / total_users * 100) if total_users > 0 else 0
        
        # Connexions récentes (24h)
        from app.models.oauth import OAuthLoginAttempt
        recent_threshold = datetime.utcnow() - timedelta(hours=24)
        recent_logins = db.query(OAuthLoginAttempt).filter(
            OAuthLoginAttempt.created_at >= recent_threshold,
            OAuthLoginAttempt.success == True
        ).count()
        
        return OAuthStatsResponse(
            total_oauth_users=total_oauth_users,
            google_users=google_users,
            github_users=github_users,
            microsoft_users=microsoft_users,
            oauth_registration_rate=round(oauth_registration_rate, 2),
            recent_logins=recent_logins
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques OAuth2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques OAuth2"
        )


# Import pour la génération de mot de passe aléatoire
import secrets