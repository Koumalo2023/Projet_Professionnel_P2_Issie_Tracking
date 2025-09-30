# app/models/mfa.py
"""
Modèles de données pour l'authentification multi-facteurs (MFA)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.database.database import Base


class MFASettings(Base):
    """Paramètres MFA pour un utilisateur"""
    
    __tablename__ = "mfa_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    method = Column(String(20), default="totp", nullable=False)  # totp, sms, email
    secret_key = Column(String(32), nullable=True)  # Clé secrète pour TOTP
    backup_codes = Column(Text, nullable=True)  # Codes de secours JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="mfa_settings")


class MFALoginAttempt(Base):
    """Tentatives de connexion MFA pour le suivi de sécurité"""
    
    __tablename__ = "mfa_login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attempt_type = Column(String(20), nullable=False)  # setup, login, recovery
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="mfa_login_attempts")


class MFARecoveryCode(Base):
    """Codes de récupération MFA pour les cas d'urgence"""
    
    __tablename__ = "mfa_recovery_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code_hash = Column(String(128), nullable=False)  # Code hashé pour sécurité
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="mfa_recovery_codes")