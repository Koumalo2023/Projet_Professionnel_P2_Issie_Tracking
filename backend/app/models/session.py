# backend/app/models/session.py
"""
Modèle pour la gestion des sessions utilisateur
Suivi des connexions actives et historique des sessions
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.database.database import Base


class UserSession(Base):
    """Modèle pour le suivi des sessions utilisateur actives"""
    
    __tablename__ = "user_sessions"
    
    # Identifiant unique de la session
    id = Column(Integer, primary_key=True, index=True)
    
    # Référence à l'utilisateur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Token de session (JWT ou autre identifiant unique)
    session_token = Column(String(512), unique=True, index=True, nullable=False)
    
    # Informations sur le client
    ip_address = Column(String(45), nullable=False)  # Support IPv6
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)  # web, mobile, tablet
    browser = Column(String(100), nullable=True)
    platform = Column(String(50), nullable=True)  # windows, linux, mac, android, ios
    
    # Métadonnées de la session
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Statut de la session
    is_active = Column(Boolean, default=True, nullable=False)
    is_mobile = Column(Boolean, default=False, nullable=False)
    
    # Sécurité
    refresh_token = Column(String(512), unique=True, index=True, nullable=True)
    csrf_token = Column(String(128), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="sessions")
    
    # Index composites pour les performances
    __table_args__ = (
        Index('idx_user_active_sessions', 'user_id', 'is_active'),
        Index('idx_session_expires', 'expires_at'),
        Index('idx_session_token', 'session_token'),
    )
    
    def is_expired(self) -> bool:
        """Vérifie si la session est expirée"""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """Met à jour le timestamp de dernière activité"""
        self.last_activity = datetime.utcnow()
    
    def get_session_info(self) -> dict:
        """Retourne les informations de la session sous forme de dictionnaire"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "browser": self.browser,
            "platform": self.platform,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active,
            "is_mobile": self.is_mobile
        }


class LoginHistory(Base):
    """Historique des connexions utilisateur"""
    
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Type de connexion
    login_type = Column(String(50), nullable=False)  # password, oauth_google, oauth_github, etc.
    provider = Column(String(50), nullable=True)  # Pour OAuth2
    
    # Informations de connexion
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)  # Géolocalisation approximative
    success = Column(Boolean, default=True, nullable=False)
    
    # Détails en cas d'échec
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    login_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    logout_at = Column(DateTime, nullable=True)
    
    # Session associée (si disponible)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="login_history")
    session = relationship("UserSession")
    
    # Index pour les requêtes fréquentes
    __table_args__ = (
        Index('idx_login_user_date', 'user_id', 'login_at'),
        Index('idx_login_type', 'login_type'),
        Index('idx_login_success', 'success'),
    )
    
    def get_duration(self) -> timedelta:
        """Calcule la durée de la session si logout_at est défini"""
        if self.logout_at:
            return self.logout_at - self.login_at
        return datetime.utcnow() - self.login_at


class SecurityEvent(Base):
    """Événements de sécurité liés aux sessions"""
    
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Type d'événement
    event_type = Column(String(100), nullable=False)  # session_created, session_expired, suspicious_activity, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Détails de l'événement
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Métadonnées
    metadata = Column(Text, nullable=True)  # JSON supplémentaire
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Session associée (si disponible)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="security_events")
    session = relationship("UserSession")
    
    # Index pour l'analyse de sécurité
    __table_args__ = (
        Index('idx_security_event_type', 'event_type'),
        Index('idx_security_severity', 'severity'),
        Index('idx_security_created', 'created_at'),
    )


# Mise à jour du modèle User pour inclure les relations
"""
Ajouter ces relations au modèle User existant (app/models/user.py):

sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")
"""