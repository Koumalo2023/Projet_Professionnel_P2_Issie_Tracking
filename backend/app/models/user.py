
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer)
    can_be_contacted = Column(Boolean, default=False)
    can_data_be_shared = Column(Boolean, default=False)
    
    # Nouveaux champs pour le profil avancé
    profile_picture = Column(String, nullable=True)  # URL de la photo de profil
    biography = Column(Text, nullable=True)          # Biographie de l'utilisateur
    location = Column(String, nullable=True)         # Localisation
    website = Column(String, nullable=True)          # Site web personnel
    company = Column(String, nullable=True)          # Entreprise
    job_title = Column(String, nullable=True)        # Poste
    social_links = Column(JSON, nullable=True)       # Liens sociaux (JSON)
    
    # Métadonnées du profil
    profile_updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    profile_visibility = Column(String, default="public")  # public, private, contacts_only

    # Relations existantes
    projects = relationship("Project", back_populates="author")
    issues = relationship("Issue", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    contributions = relationship("Contributor", back_populates="user")
    
    # Nouvelles relations RBAC
    user_roles = relationship("UserRole", back_populates="user")
    project_roles = relationship("ProjectRole", back_populates="user")
    
    # Relations MFA
    mfa_settings = relationship("MFASettings", back_populates="user", uselist=False)
    mfa_login_attempts = relationship("MFALoginAttempt", back_populates="user")
    mfa_recovery_codes = relationship("MFARecoveryCode", back_populates="user")
    
    # Relations OAuth2
    oauth_accounts = relationship("OAuthUser", back_populates="user", cascade="all, delete-orphan")
    
    # Relations sessions
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")
    
    # Relations pour le profil avancé
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("UserExperience", back_populates="user", cascade="all, delete-orphan")
    educations = relationship("UserEducation", back_populates="user", cascade="all, delete-orphan")