# app/models/oauth.py
"""
Modèles de données pour l'authentification OAuth2
Gestion des connexions via Google, GitHub, Microsoft
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.database import Base


class OAuthProvider(Base):
    """Fournisseurs OAuth2 supportés"""
    
    __tablename__ = "oauth_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # google, github, microsoft
    display_name = Column(String(100), nullable=False)      # Google, GitHub, Microsoft
    client_id = Column(String(500), nullable=True)          # Client ID du provider
    client_secret = Column(String(500), nullable=True)      # Client Secret (chiffré)
    authorization_url = Column(String(500), nullable=False)
    token_url = Column(String(500), nullable=False)
    userinfo_url = Column(String(500), nullable=False)
    scope = Column(String(500), nullable=False)             # Scopes demandés
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OAuthUser(Base):
    """Associations entre utilisateurs et comptes OAuth2"""
    
    __tablename__ = "oauth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("oauth_providers.id"), nullable=False)
    provider_user_id = Column(String(255), nullable=False)  # ID unique du user chez le provider
    email = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)              # Token d'accès (chiffré)
    refresh_token = Column(Text, nullable=True)             # Refresh token (chiffré)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    profile_data = Column(Text, nullable=True)              # Données du profil (JSON)
    is_primary = Column(Boolean, default=False, nullable=False)  # Méthode de connexion principale
    
    # Relations
    user = relationship("User", back_populates="oauth_accounts")
    provider = relationship("OAuthProvider")
    
    # Index unique pour éviter les doublons
    __table_args__ = (
        (UniqueConstraint('provider_id', 'provider_user_id', name='uq_provider_user')),
        (UniqueConstraint('user_id', 'provider_id', name='uq_user_provider')),
    )


class OAuthState(Base):
    """Stockage des états OAuth2 pour la sécurité CSRF"""
    
    __tablename__ = "oauth_states"
    
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(128), unique=True, nullable=False)  # Token state unique
    provider = Column(String(50), nullable=False)            # Provider concerné
    redirect_uri = Column(String(500), nullable=True)        # URI de redirection
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Expiration après 10 min


class OAuthLoginAttempt(Base):
    """Tentatives de connexion OAuth2 pour le suivi de sécurité"""
    
    __tablename__ = "oauth_login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())