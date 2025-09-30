# backend/app/schemas/user_profile_schema.py
"""
Schémas Pydantic pour les profils utilisateurs avancés
Gestion de la photo, biographie, compétences, expériences et formations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProfileVisibility(str, Enum):
    """Visibilité du profil utilisateur"""
    PUBLIC = "public"
    PRIVATE = "private"
    CONTACTS_ONLY = "contacts_only"


class SkillLevel(str, Enum):
    """Niveaux de compétence"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EmploymentType(str, Enum):
    """Types d'emploi"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class LanguageProficiency(str, Enum):
    """Niveaux de maîtrise des langues"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    FLUENT = "fluent"
    NATIVE = "native"


# Schémas de base pour le profil utilisateur
class UserProfileBase(BaseModel):
    """Schéma de base pour le profil utilisateur"""
    profile_picture: Optional[str] = Field(None, description="URL de la photo de profil")
    biography: Optional[str] = Field(None, description="Biographie de l'utilisateur")
    location: Optional[str] = Field(None, description="Localisation")
    website: Optional[str] = Field(None, description="Site web personnel")
    company: Optional[str] = Field(None, description="Entreprise")
    job_title: Optional[str] = Field(None, description="Poste")
    social_links: Optional[Dict[str, str]] = Field(None, description="Liens sociaux")
    profile_visibility: ProfileVisibility = Field(ProfileVisibility.PUBLIC, description="Visibilité du profil")


class UserProfileUpdate(UserProfileBase):
    """Schéma pour mettre à jour le profil utilisateur"""
    pass


class UserProfileResponse(UserProfileBase):
    """Schéma de réponse pour le profil utilisateur"""
    id: int
    username: str
    email: str
    age: Optional[int]
    can_be_contacted: bool
    can_data_be_shared: bool
    profile_updated_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour les compétences
class UserSkillBase(BaseModel):
    """Schéma de base pour une compétence utilisateur"""
    skill_name: str = Field(..., max_length=100, description="Nom de la compétence")
    skill_level: SkillLevel = Field(SkillLevel.INTERMEDIATE, description="Niveau de compétence")
    category: Optional[str] = Field(None, max_length=50, description="Catégorie de compétence")
    years_of_experience: Optional[float] = Field(0, ge=0, description="Années d'expérience")
    is_verified: bool = Field(False, description="Compétence vérifiée")


class UserSkillCreate(UserSkillBase):
    """Schéma pour créer une compétence utilisateur"""
    pass


class UserSkillUpdate(BaseModel):
    """Schéma pour mettre à jour une compétence utilisateur"""
    skill_level: Optional[SkillLevel] = None
    category: Optional[str] = None
    years_of_experience: Optional[float] = None
    is_verified: Optional[bool] = None


class UserSkillResponse(UserSkillBase):
    """Schéma de réponse pour une compétence utilisateur"""
    id: int
    user_id: int
    verified_by: Optional[int]
    verification_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour les expériences professionnelles
class UserExperienceBase(BaseModel):
    """Schéma de base pour une expérience professionnelle"""
    company: str = Field(..., max_length=200, description="Entreprise")
    job_title: str = Field(..., max_length=200, description="Poste")
    description: Optional[str] = Field(None, description="Description du poste")
    location: Optional[str] = Field(None, max_length=100, description="Localisation")
    start_date: datetime = Field(..., description="Date de début")
    end_date: Optional[datetime] = Field(None, description="Date de fin")
    is_current: bool = Field(False, description="Poste actuel")
    employment_type: EmploymentType = Field(EmploymentType.FULL_TIME, description="Type d'emploi")
    skills_used: Optional[List[str]] = Field(None, description="Compétences utilisées")


class UserExperienceCreate(UserExperienceBase):
    """Schéma pour créer une expérience professionnelle"""
    pass


class UserExperienceUpdate(BaseModel):
    """Schéma pour mettre à jour une expérience professionnelle"""
    company: Optional[str] = None
    job_title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    employment_type: Optional[EmploymentType] = None
    skills_used: Optional[List[str]] = None


class UserExperienceResponse(UserExperienceBase):
    """Schéma de réponse pour une expérience professionnelle"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour les formations
class UserEducationBase(BaseModel):
    """Schéma de base pour une formation"""
    institution: str = Field(..., max_length=200, description="Établissement")
    degree: str = Field(..., max_length=200, description="Diplôme")
    field_of_study: Optional[str] = Field(None, max_length=200, description="Domaine d'étude")
    description: Optional[str] = Field(None, description="Description de la formation")
    start_date: datetime = Field(..., description="Date de début")
    end_date: Optional[datetime] = Field(None, description="Date de fin")
    is_current: bool = Field(False, description="Formation en cours")
    grade: Optional[str] = Field(None, max_length=50, description="Note/moyenne")
    activities: Optional[str] = Field(None, description="Activités extrascolaires")


class UserEducationCreate(UserEducationBase):
    """Schéma pour créer une formation"""
    pass


class UserEducationUpdate(BaseModel):
    """Schéma pour mettre à jour une formation"""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    grade: Optional[str] = None
    activities: Optional[str] = None


class UserEducationResponse(UserEducationBase):
    """Schéma de réponse pour une formation"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour les certifications
class UserCertificationBase(BaseModel):
    """Schéma de base pour une certification"""
    name: str = Field(..., max_length=200, description="Nom de la certification")
    issuing_organization: str = Field(..., max_length=200, description="Organisme émetteur")
    credential_id: Optional[str] = Field(None, max_length=100, description="Numéro de certification")
    credential_url: Optional[str] = Field(None, max_length=500, description="Lien vers la certification")
    issue_date: datetime = Field(..., description="Date d'obtention")
    expiration_date: Optional[datetime] = Field(None, description="Date d'expiration")
    does_not_expire: bool = Field(False, description="Certification sans expiration")


class UserCertificationCreate(UserCertificationBase):
    """Schéma pour créer une certification"""
    pass


class UserCertificationUpdate(BaseModel):
    """Schéma pour mettre à jour une certification"""
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    does_not_expire: Optional[bool] = None


class UserCertificationResponse(UserCertificationBase):
    """Schéma de réponse pour une certification"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour les projets personnels
class UserProjectBase(BaseModel):
    """Schéma de base pour un projet personnel"""
    name: str = Field(..., max_length=200, description="Nom du projet")
    description: Optional[str] = Field(None, description="Description du projet")
    project_url: Optional[str] = Field(None, max_length=500, description="Lien vers le projet")
    repository_url: Optional[str] = Field(None, max_length=500, description="Lien vers le dépôt")
    start_date: datetime = Field(..., description="Date de début")
    end_date: Optional[datetime] = Field(None, description="Date de fin")
    is_current: bool = Field(False, description="Projet en cours")
    technologies: Optional[List[str]] = Field(None, description="Technologies utilisées")
    skills_used: Optional[List[str]] = Field(None, description="Compétences utilisées")


class UserProjectCreate(UserProjectBase):
    """Schéma pour créer un projet personnel"""
    pass


class UserProjectUpdate(BaseModel):
    """Schéma pour mettre à jour un projet personnel"""
    name: Optional[str] = None
    description: Optional[str] = None
    project_url: Optional[str] = None
    repository_url: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: Optional[bool] = None
    technologies: Optional[List[str]] = None
    skills_used: Optional[List[str]] = None


class UserProjectResponse(UserProjectBase):
    """Schéma de réponse pour un projet personnel"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour les langues
class UserLanguageBase(BaseModel):
    """Schéma de base pour une langue"""
    language: str = Field(..., max_length=100, description="Langue")
    proficiency: LanguageProficiency = Field(LanguageProficiency.INTERMEDIATE, description="Niveau de maîtrise")


class UserLanguageCreate(UserLanguageBase):
    """Schéma pour créer une langue"""
    pass


class UserLanguageUpdate(BaseModel):
    """Schéma pour mettre à jour une langue"""
    language: Optional[str] = None
    proficiency: Optional[LanguageProficiency] = None


class UserLanguageResponse(UserLanguageBase):
    """Schéma de réponse pour une langue"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schémas de réponse complets
class UserProfileCompleteResponse(UserProfileResponse):
    """Schéma de réponse complet du profil utilisateur"""
    skills: List[UserSkillResponse] = []
    experiences: List[UserExperienceResponse] = []
    educations: List[UserEducationResponse] = []
    certifications: List[UserCertificationResponse] = []
    projects: List[UserProjectResponse] = []
    languages: List[UserLanguageResponse] = []


class ProfileStatsResponse(BaseModel):
    """Statistiques du profil utilisateur"""
    total_skills: int = Field(0, description="Nombre total de compétences")
    total_experiences: int = Field(0, description="Nombre total d'expériences")
    total_educations: int = Field(0, description="Nombre total de formations")
    total_certifications: int = Field(0, description="Nombre total de certifications")
    total_projects: int = Field(0, description="Nombre total de projets")
    total_languages: int = Field(0, description="Nombre total de langues")
    profile_completion_percentage: float = Field(0, description="Pourcentage de complétion du profil")
    profile_views: int = Field(0, description="Nombre de vues du profil")


class ProfileSearchResponse(BaseModel):
    """Résultat de recherche de profils"""
    id: int
    username: str
    profile_picture: Optional[str]
    job_title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    skills: List[str] = []
    match_score: float = Field(0, description="Score de correspondance avec la recherche")


# Schémas pour les opérations batch
class SkillBulkCreate(BaseModel):
    """Schéma pour créer plusieurs compétences en une seule requête"""
    skills: List[UserSkillCreate]


class ExperienceBulkCreate(BaseModel):
    """Schéma pour créer plusieurs expériences en une seule requête"""
    experiences: List[UserExperienceCreate]


class EducationBulkCreate(BaseModel):
    """Schéma pour créer plusieurs formations en une seule requête"""
    educations: List[UserEducationCreate]


# Schémas pour les validations
class ProfileSearchQuery(BaseModel):
    """Schéma pour les requêtes de recherche de profils"""
    skills: Optional[List[str]] = Field(None, description="Compétences recherchées")
    location: Optional[str] = Field(None, description="Localisation")
    company: Optional[str] = Field(None, description="Entreprise")
    job_title: Optional[str] = Field(None, description="Poste")
    min_experience: Optional[int] = Field(None, ge=0, description="Expérience minimale en années")
    limit: int = Field(20, le=100, description="Nombre maximum de résultats")
    offset: int = Field(0, ge=0, description="Décalage pour la pagination")