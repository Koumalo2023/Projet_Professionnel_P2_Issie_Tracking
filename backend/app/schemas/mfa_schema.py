# app/schemas/mfa_schema.py
"""
Schémas Pydantic pour l'authentification multi-facteurs (MFA)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class MFASetupRequest(BaseModel):
    """Requête pour démarrer la configuration MFA"""
    
    method: str = Field(default="totp", description="Méthode MFA (totp, sms, email)")


class MFASetupResponse(BaseModel):
    """Réponse pour la configuration MFA"""
    
    secret_key: str = Field(..., description="Clé secrète pour l'application d'authentification")
    backup_codes: List[str] = Field(..., description="Codes de secours à sauvegarder")
    method: str = Field(..., description="Méthode MFA configurée")
    qr_code_url: Optional[str] = Field(None, description="URL du QR code pour l'application d'authentification")


class MFAVerifyRequest(BaseModel):
    """Requête pour vérifier un code MFA"""
    
    code: str = Field(..., min_length=6, max_length=8, description="Code MFA à vérifier")


class MFAVerifyResponse(BaseModel):
    """Réponse pour la vérification MFA"""
    
    success: bool = Field(..., description="Indique si la vérification a réussi")
    message: str = Field(..., description="Message de statut")


class MFAStatusResponse(BaseModel):
    """Réponse pour le statut MFA"""
    
    is_enabled: bool = Field(..., description="Indique si le MFA est activé")
    is_setup: bool = Field(..., description="Indique si le MFA est configuré")
    method: Optional[str] = Field(None, description="Méthode MFA configurée")
    setup_required: bool = Field(..., description="Indique si la configuration est requise")


class MFARecoveryCodesResponse(BaseModel):
    """Réponse pour la génération de codes de récupération"""
    
    recovery_codes: List[str] = Field(..., description="Nouveaux codes de récupération")
    message: str = Field(..., description="Instructions pour l'utilisation")


class MFALoginAttemptResponse(BaseModel):
    """Réponse pour les tentatives de connexion MFA"""
    
    id: int
    user_id: int
    attempt_type: str
    ip_address: str
    success: bool
    failure_reason: Optional[str]
    created_at: str


class MFASettingsResponse(BaseModel):
    """Réponse pour les paramètres MFA"""
    
    id: int
    user_id: int
    is_enabled: bool
    method: str
    created_at: str
    updated_at: str


class MFAEnableRequest(BaseModel):
    """Requête pour activer le MFA"""
    
    code: str = Field(..., min_length=6, max_length=6, description="Code MFA de vérification")


class MFADisableRequest(BaseModel):
    """Requête pour désactiver le MFA"""
    
    password: str = Field(..., description="Mot de passe de confirmation")


class MFALoginRequest(BaseModel):
    """Requête pour la connexion avec MFA"""
    
    username: str = Field(..., description="Nom d'utilisateur")
    password: str = Field(..., description="Mot de passe")
    mfa_code: Optional[str] = Field(None, description="Code MFA (requis si MFA activé)")


class MFALoginResponse(BaseModel):
    """Réponse pour la connexion avec MFA"""
    
    access_token: str = Field(..., description="Token d'accès JWT")
    token_type: str = Field(default="bearer", description="Type de token")
    requires_mfa: bool = Field(..., description="Indique si la vérification MFA est requise")
    mfa_setup_required: bool = Field(..., description="Indique si la configuration MFA est requise")
    user_id: int = Field(..., description="ID de l'utilisateur")


class MFAQRCodeResponse(BaseModel):
    """Réponse pour la génération de QR code"""
    
    qr_code_url: str = Field(..., description="URL du QR code")
    secret_key: str = Field(..., description="Clé secrète pour configuration manuelle")
    provisioning_uri: str = Field(..., description="URI de provisionnement pour applications d'authentification")


class MFABackupCodesRequest(BaseModel):
    """Requête pour régénérer les codes de secours"""
    
    password: str = Field(..., description="Mot de passe de confirmation")


class MFARecoveryRequest(BaseModel):
    """Requête pour utiliser un code de récupération"""
    
    recovery_code: str = Field(..., min_length=8, max_length=8, description="Code de récupération")


class MFAStatsResponse(BaseModel):
    """Réponse pour les statistiques MFA"""
    
    total_users: int = Field(..., description="Nombre total d'utilisateurs")
    mfa_enabled_users: int = Field(..., description="Nombre d'utilisateurs avec MFA activé")
    mfa_setup_users: int = Field(..., description="Nombre d'utilisateurs avec MFA configuré")
    mfa_usage_rate: float = Field(..., description="Taux d'utilisation du MFA")
    recent_attempts: int = Field(..., description="Tentatives récentes (24h)")


# Schémas pour la documentation API
class MFAErrorResponse(BaseModel):
    """Schéma pour les erreurs MFA"""
    
    error: str = Field(..., description="Type d'erreur")
    detail: str = Field(..., description="Description de l'erreur")
    error_code: str = Field(..., description="Code d'erreur")


class MFASuccessResponse(BaseModel):
    """Schéma pour les réponses de succès MFA"""
    
    success: bool = Field(..., description="Indicateur de succès")
    message: str = Field(..., description="Message de succès")
    data: Optional[Dict[str, Any]] = Field(None, description="Données supplémentaires")