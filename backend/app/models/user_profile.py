# backend/app/models/user_profile.py
"""
Modèles pour les profils utilisateurs avancés
Gestion des compétences, expériences professionnelles et formations
"""

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.database import Base


class UserSkill(Base):
    """Compétences d'un utilisateur"""
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)  # Nom de la compétence
    skill_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced, expert
    category = Column(String(50), nullable=True)  # Catégorie (programming, design, management, etc.)
    years_of_experience = Column(Float, default=0)  # Années d'expérience
    is_verified = Column(Boolean, default=False)  # Compétence vérifiée
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Qui a vérifié
    verification_date = Column(DateTime, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="skills", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])


class UserExperience(Base):
    """Expériences professionnelles d'un utilisateur"""
    __tablename__ = "user_experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations sur l'expérience
    company = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    
    # Période
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL = poste actuel
    is_current = Column(Boolean, default=False)
    
    # Type d'emploi
    employment_type = Column(String(50), default="full_time")  # full_time, part_time, contract, internship
    
    # Compétences utilisées
    skills_used = Column(JSON, nullable=True)  # Liste des compétences utilisées
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="experiences")


class UserEducation(Base):
    """Formations et éducations d'un utilisateur"""
    __tablename__ = "user_educations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations sur l'éducation
    institution = Column(String(200), nullable=False)
    degree = Column(String(200), nullable=False)
    field_of_study = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Période
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL = en cours
    is_current = Column(Boolean, default=False)
    
    # Notes et résultats
    grade = Column(String(50), nullable=True)  # Note/moyenne
    activities = Column(Text, nullable=True)  # Activités extrascolaires
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="educations")


class UserCertification(Base):
    """Certifications professionnelles d'un utilisateur"""
    __tablename__ = "user_certifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations sur la certification
    name = Column(String(200), nullable=False)
    issuing_organization = Column(String(200), nullable=False)
    credential_id = Column(String(100), nullable=True)  # Numéro de certification
    credential_url = Column(String(500), nullable=True)  # Lien vers la certification
    
    # Dates
    issue_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)  # NULL = pas d'expiration
    does_not_expire = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User")


class UserProject(Base):
    """Projets personnels ou professionnels d'un utilisateur"""
    __tablename__ = "user_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations sur le projet
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project_url = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)
    
    # Période
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL = en cours
    is_current = Column(Boolean, default=False)
    
    # Technologies utilisées
    technologies = Column(JSON, nullable=True)  # Liste des technologies
    skills_used = Column(JSON, nullable=True)   # Liste des compétences
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User")


class UserLanguage(Base):
    """Langues parlées par l'utilisateur"""
    __tablename__ = "user_languages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations sur la langue
    language = Column(String(100), nullable=False)
    proficiency = Column(String(50), default="intermediate")  # beginner, intermediate, advanced, fluent, native
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User")