# app/services/oauth_service.py
"""
Service pour l'authentification OAuth2
Gestion des connexions via Google, GitHub, Microsoft
"""

import json
import secrets
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import requests
from urllib.parse import urlencode

from app.models.oauth import OAuthProvider, OAuthUser, OAuthState, OAuthLoginAttempt
from app.models.user import User
from app.auth.auth_utils import create_access_token, get_password_hash
from app.utils.logger import get_logger
from app.exceptions.oauth_exceptions import (
    OAuthProviderNotConfiguredException,
    OAuthStateNotFoundException,
    OAuthStateExpiredException,
    OAuthInvalidCodeException,
    OAuthUserNotFoundException,
    OAuthProviderException
)
from oauth_config import OAuthConfig

logger = get_logger(__name__)


class OAuthService:
    """Service de gestion de l'authentification OAuth2"""
    
    def __init__(self, db: Session):
        self.db = db
        self.providers_config = self._load_providers_config()
    
    def _load_providers_config(self) -> Dict[str, Dict[str, Any]]:
        """Charge la configuration des providers OAuth2 depuis OAuthConfig"""
        configs = {}
        
        for provider in ["google", "github", "microsoft"]:
            config = OAuthConfig.get_provider_config(provider)
            if config.get("client_id") and config.get("client_secret"):
                configs[provider] = config
        
        return configs
    
    def get_authorization_url(self, provider: str, redirect_uri: str) -> str:
        """
        Génère l'URL d'autorisation OAuth2
        
        Args:
            provider: Nom du provider (google, github, microsoft)
            redirect_uri: URI de redirection après authentification
            
        Returns:
            URL d'autorisation complète
        """
        if provider not in self.providers_config:
            raise OAuthProviderNotConfiguredException(provider)
        
        config = self.providers_config[provider]
        
        # Génère un state sécurisé
        state = secrets.token_urlsafe(32)
        
        # Stocke le state en base pour vérification ultérieure
        oauth_state = OAuthState(
            state=state,
            provider=provider,
            redirect_uri=redirect_uri,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        self.db.add(oauth_state)
        self.db.commit()
        
        # Paramètres pour l'URL d'autorisation
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": config["scope"],
            "state": state,
            "access_type": "offline" if provider == "google" else None,
            "prompt": "consent" if provider == "google" else None,
        }
        
        # Nettoie les paramètres None
        params = {k: v for k, v in params.items() if v is not None}
        
        # Construit l'URL d'autorisation
        authorization_url = f"{config['authorization_url']}?{urlencode(params)}"
        
        return authorization_url, state
    
    def verify_state(self, state: str, provider: str) -> bool:
        """
        Vérifie la validité d'un state OAuth2
        
        Args:
            state: Token state à vérifier
            provider: Provider concerné
            
        Returns:
            True si le state est valide
        """
        oauth_state = self.db.query(OAuthState).filter(
            OAuthState.state == state,
            OAuthState.provider == provider
        ).first()
        
        if not oauth_state:
            raise OAuthStateNotFoundException()
        
        if oauth_state.expires_at < datetime.utcnow():
            # Supprime le state expiré
            self.db.delete(oauth_state)
            self.db.commit()
            raise OAuthStateExpiredException()
        
        # Supprime le state utilisé
        self.db.delete(oauth_state)
        self.db.commit()
        
        return True
    
    def exchange_code_for_token(self, provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Échange le code d'autorisation contre un token d'accès
        
        Args:
            provider: Nom du provider
            code: Code d'autorisation
            redirect_uri: URI de redirection
            
        Returns:
            Données du token
        """
        if provider not in self.providers_config:
            raise OAuthProviderNotConfiguredException(provider)
        
        config = self.providers_config[provider]
        
        # Paramètres pour la requête de token
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        
        headers = {
            "Accept": "application/json",
        }
        
        if provider == "github":
            headers["Accept"] = "application/json"
        
        try:
            response = requests.post(
                config["token_url"],
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur OAuth2 {provider}: {response.status_code} - {response.text}")
                raise OAuthInvalidCodeException()
            
            token_data = response.json()
            
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Erreur réseau OAuth2 {provider}: {str(e)}")
            raise OAuthProviderException(f"Erreur de communication avec {provider}")
    
    def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """
        Récupère les informations utilisateur du provider
        
        Args:
            provider: Nom du provider
            access_token: Token d'accès
            
        Returns:
            Informations utilisateur
        """
        if provider not in self.providers_config:
            raise OAuthProviderNotConfiguredException(provider)
        
        config = self.providers_config[provider]
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        
        try:
            response = requests.get(
                config["userinfo_url"],
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur récupération userinfo {provider}: {response.status_code}")
                raise OAuthProviderException("Impossible de récupérer les informations utilisateur")
            
            user_info = response.json()
            
            # Normalise les données utilisateur selon le provider
            return self._normalize_user_info(provider, user_info)
            
        except requests.RequestException as e:
            logger.error(f"Erreur réseau userinfo {provider}: {str(e)}")
            raise OAuthProviderException(f"Erreur de communication avec {provider}")
    
    def _normalize_user_info(self, provider: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise les informations utilisateur selon le provider"""
        normalized = {
            "provider": provider,
            "provider_user_id": str(user_info.get("id") or user_info.get("sub")),
            "email": user_info.get("email", ""),
            "name": user_info.get("name", ""),
            "given_name": user_info.get("given_name", ""),
            "family_name": user_info.get("family_name", ""),
            "picture": user_info.get("picture") or user_info.get("avatar_url", ""),
            "locale": user_info.get("locale", ""),
            "email_verified": user_info.get("email_verified", False),
        }
        
        # Traitements spécifiques par provider
        if provider == "github":
            # GitHub ne retourne pas l'email vérifié par défaut
            if not normalized["email"]:
                normalized["email"] = user_info.get("login", "") + "@users.noreply.github.com"
            normalized["name"] = user_info.get("name", user_info.get("login", ""))
        
        elif provider == "microsoft":
            normalized["given_name"] = user_info.get("givenName", "")
            normalized["family_name"] = user_info.get("surname", "")
            normalized["email_verified"] = True  # Microsoft vérifie les emails
        
        elif provider == "facebook":
            # Facebook retourne les noms séparés
            normalized["given_name"] = user_info.get("first_name", "")
            normalized["family_name"] = user_info.get("last_name", "")
            normalized["name"] = f"{normalized['given_name']} {normalized['family_name']}".strip()
            normalized["email_verified"] = True  # Facebook vérifie les emails
            # Facebook ne retourne pas l'image de profil par défaut, on peut la construire
            if user_info.get("id") and not normalized["picture"]:
                normalized["picture"] = f"https://graph.facebook.com/{user_info['id']}/picture?type=large"
        
        return normalized
    
    def find_or_create_user(self, user_info: Dict[str, Any]) -> User:
        """
        Trouve ou crée un utilisateur basé sur les informations OAuth2
        
        Args:
            user_info: Informations utilisateur normalisées
            
        Returns:
            Utilisateur trouvé ou créé
        """
        provider = user_info["provider"]
        provider_user_id = user_info["provider_user_id"]
        email = user_info["email"]
        
        # Cherche d'abord l'association OAuth existante
        oauth_user = self.db.query(OAuthUser).filter(
            OAuthUser.provider_user_id == provider_user_id,
            OAuthUser.provider.has(name=provider)
        ).first()
        
        if oauth_user:
            # Met à jour les informations du profil
            oauth_user.email = email
            oauth_user.profile_data = json.dumps(user_info)
            self.db.commit()
            
            return oauth_user.user
        
        # Cherche un utilisateur existant avec le même email
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Crée un nouvel utilisateur
            user = User(
                username=self._generate_username(user_info),
                email=email,
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),  # Mot de passe aléatoire
                is_active=True,
                email_verified=user_info.get("email_verified", False)
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        
        # Crée l'association OAuth
        oauth_user = OAuthUser(
            user_id=user.id,
            provider_user_id=provider_user_id,
            email=email,
            profile_data=json.dumps(user_info)
        )
        
        # Trouve le provider dans la base
        provider_obj = self.db.query(OAuthProvider).filter(
            OAuthProvider.name == provider
        ).first()
        
        if provider_obj:
            oauth_user.provider_id = provider_obj.id
        
        self.db.add(oauth_user)
        self.db.commit()
        
        return user
    
    def _generate_username(self, user_info: Dict[str, Any]) -> str:
        """Génère un nom d'utilisateur unique basé sur les informations OAuth2"""
        base_username = user_info.get("given_name", "").lower() or user_info.get("name", "").lower()
        base_username = "".join(c for c in base_username if c.isalnum() or c in ['_', '-'])
        
        if not base_username:
            base_username = "user"
        
        # Vérifie si le nom d'utilisateur existe déjà
        username = base_username
        counter = 1
        
        while self.db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def link_oauth_account(self, user: User, user_info: Dict[str, Any]) -> OAuthUser:
        """
        Lie un compte OAuth2 à un utilisateur existant
        
        Args:
            user: Utilisateur existant
            user_info: Informations OAuth2
            
        Returns:
            Association OAuth créée
        """
        provider = user_info["provider"]
        provider_user_id = user_info["provider_user_id"]
        
        # Vérifie si l'association existe déjà
        existing_oauth = self.db.query(OAuthUser).filter(
            OAuthUser.provider_user_id == provider_user_id,
            OAuthUser.provider.has(name=provider)
        ).first()
        
        if existing_oauth:
            # Si l'association existe mais pour un autre utilisateur
            if existing_oauth.user_id != user.id:
                raise OAuthProviderException("Ce compte OAuth2 est déjà lié à un autre utilisateur")
            return existing_oauth
        
        # Crée la nouvelle association
        oauth_user = OAuthUser(
            user_id=user.id,
            provider_user_id=provider_user_id,
            email=user_info["email"],
            profile_data=json.dumps(user_info)
        )
        
        # Trouve le provider
        provider_obj = self.db.query(OAuthProvider).filter(
            OAuthProvider.name == provider
        ).first()
        
        if provider_obj:
            oauth_user.provider_id = provider_obj.id
        
        self.db.add(oauth_user)
        self.db.commit()
        
        return oauth_user
    
    def unlink_oauth_account(self, user: User, provider: str) -> bool:
        """
        Dissocie un compte OAuth2 d'un utilisateur
        
        Args:
            user: Utilisateur
            provider: Provider à dissocier
            
        Returns:
            True si la dissociation a réussi
        """
        oauth_user = self.db.query(OAuthUser).filter(
            OAuthUser.user_id == user.id,
            OAuthUser.provider.has(name=provider)
        ).first()
        
        if not oauth_user:
            raise OAuthUserNotFoundException()
        
        self.db.delete(oauth_user)
        self.db.commit()
        
        return True
    
    def get_user_oauth_accounts(self, user: User) -> List[OAuthUser]:
        """
        Récupère tous les comptes OAuth2 liés à un utilisateur
        
        Args:
            user: Utilisateur
            
        Returns:
            Liste des associations OAuth
        """
        return self.db.query(OAuthUser).filter(
            OAuthUser.user_id == user.id
        ).all()
    
    def log_oauth_attempt(self, provider: str, provider_user_id: Optional[str], 
                         email: Optional[str], ip_address: str, user_agent: Optional[str],
                         success: bool, failure_reason: Optional[str] = None) -> None:
        """Journalise une tentative de connexion OAuth2"""
        attempt = OAuthLoginAttempt(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        self.db.add(attempt)
        self.db.commit()


# Dépendance FastAPI
def get_oauth_service(db: Session) -> OAuthService:
    """Dépendance pour obtenir le service OAuth2"""
    return OAuthService(db)