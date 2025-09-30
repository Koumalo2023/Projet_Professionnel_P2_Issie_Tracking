# backend/app/schemas/token_schema.py
"""
Schémas Pydantic pour la gestion des tokens et le rafraîchissement automatique
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TokenRefreshRequest(BaseModel):
    """Requête pour rafraîchir les tokens"""
    refresh_token: str = Field(..., description="Token de rafraîchissement")
    ip_address: Optional[str] = Field(None, description="Adresse IP du client")
    user_agent: Optional[str] = Field(None, description="User-Agent du navigateur")


class TokenResponse(BaseModel):
    """Réponse contenant les tokens rafraîchis"""
    access_token: str = Field(..., description="Nouveau token d'accès")
    refresh_token: str = Field(..., description="Nouveau token de rafraîchissement")
    token_type: str = Field("bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée d'expiration en secondes")
    session_id: int = Field(..., description="ID de la session")


class TokenRevokeRequest(BaseModel):
    """Requête pour révoquer des tokens"""
    session_id: Optional[int] = Field(None, description="ID de session spécifique à révoquer")
    revoke_all: bool = Field(False, description="Révoquer toutes les sessions de l'utilisateur")


class TokenRevokeResponse(BaseModel):
    """Réponse après révocation des tokens"""
    message: str = Field(..., description="Message de confirmation")
    revoked_count: int = Field(0, description="Nombre de sessions révoquées")


class TokenMetricsResponse(BaseModel):
    """Métriques des tokens pour un utilisateur"""
    active_sessions: int = Field(..., description="Nombre de sessions actives")
    soon_expiring_sessions: int = Field(..., description="Sessions expirant bientôt")
    max_allowed_sessions: int = Field(..., description="Nombre maximum de sessions autorisées")
    access_token_duration_minutes: int = Field(..., description="Durée du token d'accès en minutes")
    refresh_token_duration_days: int = Field(..., description="Durée du token de rafraîchissement en jours")
    can_create_new_session: bool = Field(..., description="Si l'utilisateur peut créer une nouvelle session")


class TokenCleanupStats(BaseModel):
    """Statistiques de nettoyage des tokens"""
    expired_sessions_cleaned: int = Field(..., description="Sessions expirées nettoyées")
    expired_refresh_tokens_cleaned: int = Field(..., description="Tokens de rafraîchissement expirés nettoyés")
    total_cleaned: int = Field(..., description="Total des éléments nettoyés")
    cleanup_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage du nettoyage")


class TokenValidationResponse(BaseModel):
    """Réponse de validation de token"""
    is_valid: bool = Field(..., description="Si le token est valide")
    user_id: Optional[int] = Field(None, description="ID de l'utilisateur")
    session_id: Optional[int] = Field(None, description="ID de la session")
    username: Optional[str] = Field(None, description="Nom d'utilisateur")
    expires_at: Optional[datetime] = Field(None, description="Date d'expiration")
    remaining_seconds: Optional[int] = Field(None, description="Secondes restantes avant expiration")


class TokenRotationConfig(BaseModel):
    """Configuration de la rotation des tokens"""
    access_token_expire_minutes: int = Field(15, description="Durée d'expiration du token d'accès en minutes")
    refresh_token_expire_days: int = Field(7, description="Durée d'expiration du token de rafraîchissement en jours")
    max_refresh_tokens_per_user: int = Field(5, description="Nombre maximum de tokens de rafraîchissement par utilisateur")
    automatic_rotation_enabled: bool = Field(True, description="Rotation automatique activée")
    enforce_single_session: bool = Field(False, description="Forcer une seule session par utilisateur")