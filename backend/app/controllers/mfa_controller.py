# app/controllers/mfa_controller.py
"""
Contrôleur pour l'authentification multi-facteurs (MFA)
Endpoints pour la configuration, vérification et gestion du MFA
"""

import urllib.parse
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.mfa_service import MFAService, get_mfa_service
from app.auth.auth_utils import get_current_user
from app.models.user import User
from app.schemas.mfa_schema import (
    MFASetupRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    MFAStatusResponse,
    MFARecoveryCodesResponse,
    MFAEnableRequest,
    MFADisableRequest,
    MFALoginAttemptResponse,
    MFASettingsResponse,
    MFAStatsResponse
)
from app.exceptions.mfa_exceptions import (
    MFAAlreadyEnabledException,
    MFANotEnabledException,
    MFAInvalidCodeException,
    MFANotConfiguredException
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/mfa", tags=["MFA"])


def _generate_qr_code_url(username: str, secret_key: str) -> str:
    """
    Génère l'URL du QR code pour les applications d'authentification
    
    Format: otpauth://totp/IssieTracking:{username}?secret={secret_key}&issuer=IssieTracking
    """
    # Encode les paramètres pour l'URL
    encoded_username = urllib.parse.quote(username)
    encoded_secret = urllib.parse.quote(secret_key)
    encoded_issuer = urllib.parse.quote("IssieTracking")
    
    # Construit l'URL du QR code
    qr_code_url = (
        f"otpauth://totp/IssieTracking:{encoded_username}"
        f"?secret={encoded_secret}"
        f"&issuer={encoded_issuer}"
        f"&algorithm=SHA1"
        f"&digits=6"
        f"&period=30"
    )
    
    return qr_code_url


@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: MFASetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Démarre la configuration du MFA pour l'utilisateur connecté
    
    Retourne la clé secrète et les codes de secours pour configuration
    """
    try:
        setup_data = mfa_service.setup_mfa(current_user, request.method)
        
        # Génère l'URL du QR code pour les applications d'authentification
        qr_code_url = _generate_qr_code_url(
            current_user.username, 
            setup_data["secret_key"]
        )
        
        return MFASetupResponse(
            secret_key=setup_data["secret_key"],
            backup_codes=setup_data["backup_codes"],
            method=setup_data["method"],
            qr_code_url=qr_code_url
        )
    
    except MFAAlreadyEnabledException as e:
        logger.warning(f"Tentative de configuration MFA déjà activé pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa_setup(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Vérifie le code MFA lors de la configuration initiale
    
    Active le MFA si le code est valide
    """
    try:
        success = mfa_service.verify_mfa_setup(current_user, request.code)
        
        if success:
            return MFAVerifyResponse(
                success=True,
                message="MFA configuré et activé avec succès"
            )
        else:
            return MFAVerifyResponse(
                success=False,
                message="Code MFA invalide"
            )
    
    except MFAInvalidCodeException as e:
        logger.warning(f"Code MFA invalide pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except MFANotConfiguredException as e:
        logger.warning(f"Tentative de vérification MFA non configuré pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )




@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Récupère le statut MFA de l'utilisateur connecté
    """
    try:
        status_data = mfa_service.get_mfa_status(current_user)
        
        return MFAStatusResponse(
            is_enabled=status_data["is_enabled"],
            is_setup=status_data["is_setup"],
            method=status_data["method"],
            setup_required=not status_data["is_setup"]
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut MFA pour l'utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du statut MFA"
        )


@router.post("/enable", response_model=MFAVerifyResponse)
async def enable_mfa(
    request: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Active le MFA pour l'utilisateur connecté après vérification du code
    """
    try:
        # Vérifie d'abord le code MFA
        success = mfa_service.verify_mfa_setup(current_user, request.code)
        
        if success:
            # Active le MFA
            mfa_service.enable_mfa(current_user)
            
            return MFAVerifyResponse(
                success=True,
                message="MFA activé avec succès"
            )
        else:
            return MFAVerifyResponse(
                success=False,
                message="Code MFA invalide"
            )
    
    except MFAInvalidCodeException as e:
        logger.warning(f"Code MFA invalide pour l'activation pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except MFANotConfiguredException as e:
        logger.warning(f"Tentative d'activation MFA non configuré pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/disable", response_model=MFAVerifyResponse)
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Désactive le MFA pour l'utilisateur connecté
    """
    try:
        # TODO: Vérifier le mot de passe avant de désactiver le MFA
        # Pour l'instant, on désactive sans vérification de mot de passe
        mfa_service.disable_mfa(current_user)
        
        return MFAVerifyResponse(
            success=True,
            message="MFA désactivé avec succès"
        )
    
    except MFANotEnabledException as e:
        logger.warning(f"Tentative de désactivation MFA non activé pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/recovery-codes/generate", response_model=MFARecoveryCodesResponse)
async def generate_recovery_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Génère de nouveaux codes de récupération MFA
    """
    try:
        new_codes = mfa_service.generate_new_recovery_codes(current_user)
        
        return MFARecoveryCodesResponse(
            recovery_codes=new_codes,
            message="Nouveaux codes de récupération générés. Sauvegardez-les dans un endroit sécurisé."
        )
    
    except MFANotEnabledException as e:
        logger.warning(f"Tentative de génération de codes de récupération sans MFA activé pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/settings", response_model=MFASettingsResponse)
async def get_mfa_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les paramètres MFA de l'utilisateur connecté
    """
    try:
        from app.models.mfa import MFASettings
        
        mfa_settings = db.query(MFASettings).filter(
            MFASettings.user_id == current_user.id
        ).first()
        
        if not mfa_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paramètres MFA non trouvés"
            )
        
        return MFASettingsResponse(
            id=mfa_settings.id,
            user_id=mfa_settings.user_id,
            is_enabled=mfa_settings.is_enabled,
            method=mfa_settings.method,
            created_at=mfa_settings.created_at.isoformat() if mfa_settings.created_at else None,
            updated_at=mfa_settings.updated_at.isoformat() if mfa_settings.updated_at else None
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paramètres MFA pour l'utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des paramètres MFA"
        )


@router.get("/attempts", response_model=List[MFALoginAttemptResponse])
async def get_mfa_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Récupère les dernières tentatives MFA de l'utilisateur connecté
    """
    try:
        from app.models.mfa import MFALoginAttempt
        
        attempts = db.query(MFALoginAttempt).filter(
            MFALoginAttempt.user_id == current_user.id
        ).order_by(MFALoginAttempt.created_at.desc()).limit(limit).all()
        
        return [
            MFALoginAttemptResponse(
                id=attempt.id,
                user_id=attempt.user_id,
                attempt_type=attempt.attempt_type,
                ip_address=attempt.ip_address,
                success=attempt.success,
                failure_reason=attempt.failure_reason,
                created_at=attempt.created_at.isoformat() if attempt.created_at else None
            )
            for attempt in attempts
        ]
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tentatives MFA pour l'utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des tentatives MFA"
        )


@router.post("/verify-login", response_model=MFAVerifyResponse)
async def verify_mfa_login(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Vérifie un code MFA lors de la connexion
    """
    try:
        # Dans un vrai scénario, nous récupérerions l'adresse IP de la requête
        ip_address = "127.0.0.1"  # À remplacer par request.client.host en production
        
        success = mfa_service.verify_login_code(current_user, request.code, ip_address)
        
        if success:
            return MFAVerifyResponse(
                success=True,
                message="Connexion MFA réussie"
            )
        else:
            return MFAVerifyResponse(
                success=False,
                message="Code MFA invalide"
            )
    
    except MFAInvalidCodeException as e:
        logger.warning(f"Code MFA invalide pour la connexion de l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except MFANotEnabledException as e:
        logger.warning(f"Tentative de vérification MFA non activé pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/recovery/verify", response_model=MFAVerifyResponse)
async def verify_recovery_code(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Vérifie un code de récupération MFA
    """
    try:
        # Dans un vrai scénario, nous récupérerions l'adresse IP de la requête
        ip_address = "127.0.0.1"  # À remplacer par request.client.host en production
        
        # Cette fonctionnalité est intégrée dans verify_login_code
        # Nous créons un endpoint séparé pour la clarté
        success = mfa_service.verify_login_code(current_user, request.code, ip_address)
        
        if success:
            return MFAVerifyResponse(
                success=True,
                message="Code de récupération validé avec succès"
            )
        else:
            return MFAVerifyResponse(
                success=False,
                message="Code de récupération invalide"
            )
    
    except MFAInvalidCodeException as e:
        logger.warning(f"Code de récupération invalide pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except MFANotEnabledException as e:
        logger.warning(f"Tentative d'utilisation de code de récupération sans MFA activé pour l'utilisateur {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/recovery-codes", response_model=MFARecoveryCodesResponse)
async def get_recovery_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """
    Récupère les codes de récupération actuels (uniquement lors du setup initial)
    """
    try:
        from app.models.mfa import MFASettings
        
        mfa_settings = db.query(MFASettings).filter(
            MFASettings.user_id == current_user.id
        ).first()
        
        if not mfa_settings or not mfa_settings.backup_codes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun code de récupération trouvé"
            )
        
        # IMPORTANT: En production, ne jamais renvoyer les codes réels
        # Ceci est uniquement pour le développement/démonstration
        import json
        backup_codes_hashed = json.loads(mfa_settings.backup_codes)
        
        # Pour la démonstration, nous retournons un message générique
        # En production, on ne devrait jamais exposer les codes de récupération
        return MFARecoveryCodesResponse(
            recovery_codes=["*** Masqué pour la sécurité ***"] * len(backup_codes_hashed),
            message="Les codes de récupération ne sont affichés qu'une seule fois lors de la configuration initiale"
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des codes de récupération pour l'utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des codes de récupération"
        )


@router.get("/stats", response_model=MFAStatsResponse)
async def get_mfa_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques MFA (accessible aux administrateurs uniquement)
    """
    try:
        from app.models.mfa import MFASettings, MFALoginAttempt
        from app.models.user import User
        from datetime import datetime, timedelta
        
        # Vérifier les permissions d'administrateur
        # TODO: Implémenter la vérification des permissions administrateur
        # Pour l'instant, nous autorisons tous les utilisateurs authentifiés
        
        # Statistiques de base
        total_users = db.query(User).count()
        mfa_enabled_users = db.query(MFASettings).filter(MFASettings.is_enabled == True).count()
        mfa_setup_users = db.query(MFASettings).filter(MFASettings.secret_key.isnot(None)).count()
        
        # Calcul du taux d'utilisation
        mfa_usage_rate = (mfa_enabled_users / total_users * 100) if total_users > 0 else 0
        
        # Tentatives récentes (24h)
        recent_threshold = datetime.utcnow() - timedelta(hours=24)
        recent_attempts = db.query(MFALoginAttempt).filter(
            MFALoginAttempt.created_at >= recent_threshold
        ).count()
        
        return MFAStatsResponse(
            total_users=total_users,
            mfa_enabled_users=mfa_enabled_users,
            mfa_setup_users=mfa_setup_users,
            mfa_usage_rate=round(mfa_usage_rate, 2),
            recent_attempts=recent_attempts
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des statistiques MFA"
        )
