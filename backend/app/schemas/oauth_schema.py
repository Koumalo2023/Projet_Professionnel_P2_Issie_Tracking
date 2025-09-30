# app/schemas/oauth_schema.py
"""
Schémas Pydantic pour l'authentification OAuth2
Gestion des requêtes et réponses pour les providers OAuth2
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class OAuthProviderResponse(BaseModel):
    """Réponse pour les informations du provider OAuth2"""
    
    id: int
    name: str = Field(..., description="Nom technique du provider (google, github, microsoft)")
    display_name: str = Field(..., description="Nom d'affichage du provider")
    authorization_url: str = Field(..., description="URL d'autorisation OAuth2")
    is_enabled: bool = Field(..., description="Indique si le provider est activé")
    
    class Config:
        from_attributes = True


class OAuthLoginRequest(BaseModel):
    """Requête pour initier une connexion OAuth2"""
    
    provider: str = Field(..., description="Provider OAuth2 (google, github, microsoft)")
    redirect_uri: Optional[str] = Field(None, description="URI de redirection personnalisée")


class OAuthLoginResponse(BaseModel):
    """Réponse pour l'initiation de connexion OAuth2"""
    
    authorization_url: str = Field(..., description="URL d'autorisation OAuth2")
    state: str = Field(..., description="Token state pour la sécurité CSRF")


class OAuthCallbackRequest(BaseModel):
    """Requête pour le callback OAuth2"""
    
    code: str = Field(..., description="Code d'autorisation OAuth2")
    state: str = Field(..., description="Token state pour la vérification CSRF")


class OAuthTokenResponse(BaseModel):
    """Réponse avec les tokens OAuth2"""
    
    access_token: str = Field(..., description="Token d'accès JWT")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: Optional[int] = Field(None, description="Durée de validité en secondes")
    refresh_token: Optional[str] = Field(None, description="Token de rafraîchissement")
    scope: Optional[str] = Field(None, description="Scopes accordés")


class OAuthUserInfo(BaseModel):
    """Informations utilisateur récupérées via OAuth2"""
    
    provider: str = Field(..., description="Provider OAuth2")
    provider_user_id: str = Field(..., description="ID unique de l'utilisateur chez le provider")
    email: str = Field(..., description="Email de l'utilisateur")
    name: Optional[str] = Field(None, description="Nom complet de l'utilisateur")
    given_name: Optional[str] = Field(None, description="Prénom")
    family_name: Optional[str] = Field(None, description="Nom de famille")
    picture: Optional[str] = Field(None, description="URL de l'avatar")
    locale: Optional[str] = Field(None, description="Locale de l'utilisateur")
    email_verified: Optional[bool] = Field(None, description="Email vérifié")


class OAuthAccountResponse(BaseModel):
    """Réponse pour les comptes OAuth2 liés à un utilisateur"""
    
    id: int
    provider: str = Field(..., description="Provider OAuth2")
    provider_user_id: str = Field(..., description="ID utilisateur chez le provider")
    email: str = Field(..., description="Email associé")
    is_primary: bool = Field(..., description="Méthode de connexion principale")
    created_at: datetime
    last_used: Optional[datetime] = Field(None, description="Dernière utilisation")
    
    class Config:
        from_attributes = True


class OAuthLinkRequest(BaseModel):
    """Requête pour lier un compte OAuth2 existant"""
    
    provider: str = Field(..., description="Provider OAuth2")
    code: str = Field(..., description="Code d'autorisation OAuth2")
    state: str = Field(..., description="Token state pour la vérification CSRF")


class OAuthUnlinkRequest(BaseModel):
    """Requête pour dissocier un compte OAuth2"""
    
    provider: str = Field(..., description="Provider OAuth2 à dissocier")


class OAuthLoginResult(BaseModel):
    """Résultat d'une tentative de connexion OAuth2"""
    
    success: bool = Field(..., description="Indique si la connexion a réussi")
    requires_registration: bool = Field(..., description="Indique si l'utilisateur doit s'inscrire")
    user_id: Optional[int] = Field(None, description="ID de l'utilisateur connecté")
    access_token: Optional[str] = Field(None, description="Token d'accès JWT")
    oauth_user_info: Optional[OAuthUserInfo] = Field(None, description="Informations OAuth2")
    message: Optional[str] = Field(None, description="Message d'information")


class OAuthRegistrationRequest(BaseModel):
    """Requête pour finaliser l'inscription via OAuth2"""
    
    provider: str = Field(..., description="Provider OAuth2")
    state: str = Field(..., description="Token state original")
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur choisi")
    email: str = Field(..., description="Email (doit correspondre à celui du provider)")
    accept_terms: bool = Field(..., description="Acceptation des conditions d'utilisation")


class OAuthStatsResponse(BaseModel):
    """Réponse pour les statistiques OAuth2"""
    
    total_oauth_users: int = Field(..., description="Nombre total d'utilisateurs OAuth2")
    google_users: int = Field(..., description="Utilisateurs Google")
    github_users: int = Field(..., description="Utilisateurs GitHub")
    microsoft_users: int = Field(..., description="Utilisateurs Microsoft")
    oauth_registration_rate: float = Field(..., description="Taux d'inscription via OAuth2")
    recent_logins: int = Field(..., description="Connexions récentes (24h)")


class OAuthErrorResponse(BaseModel):
    """Schéma pour les erreurs OAuth2"""
    
    error: str = Field(..., description="Type d'erreur")
    detail: str = Field(..., description="Description de l'erreur")
    error_code: str = Field(..., description="Code d'erreur")
    provider: Optional[str] = Field(None, description="Provider concerné")


class OAuthSuccessResponse(BaseModel):
    """Schéma pour les réponses de succès OAuth2"""
    
    success: bool = Field(..., description="Indicateur de succès")
    message: str = Field(..., description="Message de succès")
    data: Optional[Dict[str, Any]] = Field(None, description="Données supplémentaires")


# Configuration des providers OAuth2
class OAuthProviderConfig(BaseModel):
    """Configuration d'un provider OAuth2"""
    
    name: str
    display_name: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    userinfo_url: str
    scope: str
    is_enabled: bool = True


class OAuthProviderListResponse(BaseModel):
    """Réponse listant les providers OAuth2 disponibles"""
    
    providers: List[OAuthProviderResponse] = Field(..., description="Liste des providers")
    enabled_count: int = Field(..., description="Nombre de providers activés")