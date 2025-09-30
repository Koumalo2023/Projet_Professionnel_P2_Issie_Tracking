# backend/app/services/user_profile_service.py
"""
Service pour la gestion des profils utilisateurs avancés
Gestion de la photo, biographie, compétences, expériences et formations
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.user import User
from app.models.user_profile import (
    UserSkill, UserExperience, UserEducation, 
    UserCertification, UserProject, UserLanguage
)
from app.schemas.user_profile_schema import (
    UserProfileUpdate, UserSkillCreate, UserSkillUpdate,
    UserExperienceCreate, UserExperienceUpdate,
    UserEducationCreate, UserEducationUpdate,
    UserCertificationCreate, UserCertificationUpdate,
    UserProjectCreate, UserProjectUpdate,
    UserLanguageCreate, UserLanguageUpdate,
    ProfileSearchQuery, ProfileStatsResponse
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserProfileService:
    """Service de gestion des profils utilisateurs avancés"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Gestion du profil principal
    def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> User:
        """
        Met à jour le profil principal d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            profile_data: Données de mise à jour du profil
            
        Returns:
            Utilisateur mis à jour
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Utilisateur avec ID {user_id} non trouvé")
        
        # Met à jour les champs du profil
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Profil utilisateur {user_id} mis à jour")
        return user
    
    def get_user_profile(self, user_id: int) -> User:
        """
        Récupère le profil complet d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Utilisateur avec toutes les relations
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Utilisateur avec ID {user_id} non trouvé")
        
        return user
    
    def upload_profile_picture(self, user_id: int, file_content: bytes, filename: str) -> str:
        """
        Télécharge une photo de profil pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            file_content: Contenu du fichier
            filename: Nom du fichier original
            
        Returns:
            URL de la photo de profil
        """
        # Génère un nom de fichier unique
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"profile_{user_id}_{uuid.uuid4()}{file_extension}"
        
        # Chemin de stockage (à adapter selon l'infrastructure)
        upload_dir = "uploads/profiles"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Sauvegarde le fichier
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Met à jour le profil utilisateur
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # URL relative ou absolue selon la configuration
            profile_url = f"/static/profiles/{unique_filename}"
            user.profile_picture = profile_url
            self.db.commit()
            
            logger.info(f"Photo de profil téléchargée pour l'utilisateur {user_id}")
            return profile_url
        
        raise ValueError(f"Utilisateur avec ID {user_id} non trouvé")
    
    # Gestion des compétences
    def add_user_skill(self, user_id: int, skill_data: UserSkillCreate) -> UserSkill:
        """
        Ajoute une compétence à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            skill_data: Données de la compétence
            
        Returns:
            Compétence créée
        """
        skill = UserSkill(
            user_id=user_id,
            **skill_data.dict()
        )
        
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        
        logger.info(f"Compétence '{skill.skill_name}' ajoutée à l'utilisateur {user_id}")
        return skill
    
    def update_user_skill(self, skill_id: int, skill_data: UserSkillUpdate) -> UserSkill:
        """
        Met à jour une compétence utilisateur
        
        Args:
            skill_id: ID de la compétence
            skill_data: Données de mise à jour
            
        Returns:
            Compétence mise à jour
        """
        skill = self.db.query(UserSkill).filter(UserSkill.id == skill_id).first()
        if not skill:
            raise ValueError(f"Compétence avec ID {skill_id} non trouvée")
        
        update_data = skill_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)
        
        self.db.commit()
        self.db.refresh(skill)
        
        logger.info(f"Compétence {skill_id} mise à jour")
        return skill
    
    def delete_user_skill(self, skill_id: int) -> bool:
        """
        Supprime une compétence utilisateur
        
        Args:
            skill_id: ID de la compétence
            
        Returns:
            True si supprimée avec succès
        """
        skill = self.db.query(UserSkill).filter(UserSkill.id == skill_id).first()
        if not skill:
            raise ValueError(f"Compétence avec ID {skill_id} non trouvée")
        
        self.db.delete(skill)
        self.db.commit()
        
        logger.info(f"Compétence {skill_id} supprimée")
        return True
    
    def get_user_skills(self, user_id: int) -> List[UserSkill]:
        """
        Récupère toutes les compétences d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des compétences
        """
        return self.db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    
    # Gestion des expériences professionnelles
    def add_user_experience(self, user_id: int, experience_data: UserExperienceCreate) -> UserExperience:
        """
        Ajoute une expérience professionnelle à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            experience_data: Données de l'expérience
            
        Returns:
            Expérience créée
        """
        experience = UserExperience(
            user_id=user_id,
            **experience_data.dict()
        )
        
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        
        logger.info(f"Expérience '{experience.job_title}' ajoutée à l'utilisateur {user_id}")
        return experience
    
    def update_user_experience(self, experience_id: int, experience_data: UserExperienceUpdate) -> UserExperience:
        """
        Met à jour une expérience professionnelle
        
        Args:
            experience_id: ID de l'expérience
            experience_data: Données de mise à jour
            
        Returns:
            Expérience mise à jour
        """
        experience = self.db.query(UserExperience).filter(UserExperience.id == experience_id).first()
        if not experience:
            raise ValueError(f"Expérience avec ID {experience_id} non trouvée")
        
        update_data = experience_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(experience, field, value)
        
        self.db.commit()
        self.db.refresh(experience)
        
        logger.info(f"Expérience {experience_id} mise à jour")
        return experience
    
    def delete_user_experience(self, experience_id: int) -> bool:
        """
        Supprime une expérience professionnelle
        
        Args:
            experience_id: ID de l'expérience
            
        Returns:
            True si supprimée avec succès
        """
        experience = self.db.query(UserExperience).filter(UserExperience.id == experience_id).first()
        if not experience:
            raise ValueError(f"Expérience avec ID {experience_id} non trouvée")
        
        self.db.delete(experience)
        self.db.commit()
        
        logger.info(f"Expérience {experience_id} supprimée")
        return True
    
    def get_user_experiences(self, user_id: int) -> List[UserExperience]:
        """
        Récupère toutes les expériences d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des expériences
        """
        return self.db.query(UserExperience).filter(UserExperience.user_id == user_id).order_by(
            UserExperience.start_date.desc()
        ).all()
    
    # Gestion des formations
    def add_user_education(self, user_id: int, education_data: UserEducationCreate) -> UserEducation:
        """
        Ajoute une formation à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            education_data: Données de la formation
            
        Returns:
            Formation créée
        """
        education = UserEducation(
            user_id=user_id,
            **education_data.dict()
        )
        
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        
        logger.info(f"Formation '{education.degree}' ajoutée à l'utilisateur {user_id}")
        return education
    
    def update_user_education(self, education_id: int, education_data: UserEducationUpdate) -> UserEducation:
        """
        Met à jour une formation
        
        Args:
            education_id: ID de la formation
            education_data: Données de mise à jour
            
        Returns:
            Formation mise à jour
        """
        education = self.db.query(UserEducation).filter(UserEducation.id == education_id).first()
        if not education:
            raise ValueError(f"Formation avec ID {education_id} non trouvée")
        
        update_data = education_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(education, field, value)
        
        self.db.commit()
        self.db.refresh(education)
        
        logger.info(f"Formation {education_id} mise à jour")
        return education
    
    def delete_user_education(self, education_id: int) -> bool:
        """
        Supprime une formation
        
        Args:
            education_id: ID de la formation
            
        Returns:
            True si supprimée avec succès
        """
        education = self.db.query(UserEducation).filter(UserEducation.id == education_id).first()
        if not education:
            raise ValueError(f"Formation avec ID {education_id} non trouvée")
        
        self.db.delete(education)
        self.db.commit()
        
        logger.info(f"Formation {education_id} supprimée")
        return True
    
    def get_user_educations(self, user_id: int) -> List[UserEducation]:
        """
        Récupère toutes les formations d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des formations
        """
        return self.db.query(UserEducation).filter(UserEducation.user_id == user_id).order_by(
            UserEducation.start_date.desc()
        ).all()
    
    # Gestion des certifications
    def add_user_certification(self, user_id: int, certification_data: UserCertificationCreate) -> UserCertification:
        """
        Ajoute une certification à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            certification_data: Données de la certification
            
        Returns:
            Certification créée
        """
        certification = UserCertification(
            user_id=user_id,
            **certification_data.dict()
        )
        
        self.db.add(certification)
        self.db.commit()
        self.db.refresh(certification)
        
        logger.info(f"Certification '{certification.name}' ajoutée à l'utilisateur {user_id}")
        return certification
    
    def update_user_certification(self, certification_id: int, certification_data: UserCertificationUpdate) -> UserCertification:
        """
        Met à jour une certification
        
        Args:
            certification_id: ID de la certification
            certification_data: Données de mise à jour
            
        Returns:
            Certification mise à jour
        """
        certification = self.db.query(UserCertification).filter(UserCertification.id == certification_id).first()
        if not certification:
            raise ValueError(f"Certification avec ID {certification_id} non trouvée")
        
        update_data = certification_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(certification, field, value)
        
        self.db.commit()
        self.db.refresh(certification)
        
        logger.info(f"Certification {certification_id} mise à jour")
        return certification
    
    def delete_user_certification(self, certification_id: int) -> bool:
        """
        Supprime une certification
        
        Args:
            certification_id: ID de la certification
            
        Returns:
            True si supprimée avec succès
        """
        certification = self.db.query(UserCertification).filter(UserCertification.id == certification_id).first()
        if not certification:
            raise ValueError(f"Certification avec ID {certification_id} non trouvée")
        
        self.db.delete(certification)
        self.db.commit()
        
        logger.info(f"Certification {certification_id} supprimée")
        return True
    
    # Gestion des projets personnels
    def add_user_project(self, user_id: int, project_data: UserProjectCreate) -> UserProject:
        """
        Ajoute un projet personnel à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            project_data: Données du projet
            
        Returns:
            Projet créé
        """
        project = UserProject(
            user_id=user_id,
            **project_data.dict()
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Projet '{project.name}' ajouté à l'utilisateur {user_id}")
        return project
    
    def update_user_project(self, project_id: int, project_data: UserProjectUpdate) -> UserProject:
        """
        Met à jour un projet personnel
        
        Args:
            project_id: ID du projet
            project_data: Données de mise à jour
            
        Returns:
            Projet mis à jour
        """
        project = self.db.query(UserProject).filter(UserProject.id == project_id).first()
        if not project:
            raise ValueError(f"Projet avec ID {project_id} non trouvé")
        
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Projet {project_id} mis à jour")
        return project
    
    def delete_user_project(self, project_id: int) -> bool:
        """
        Supprime un projet personnel
        
        Args:
            project_id: ID du projet
            
        Returns:
            True si supprimé avec succès
        """
        project = self.db.query(UserProject).filter(UserProject.id == project_id).first()
        if not project:
            raise ValueError(f"Projet avec ID {project_id} non trouvé")
        
        self.db.delete(project)
        self.db.commit()
        
        logger.info(f"Projet {project_id} supprimé")
        return True
    
    # Gestion des langues
    def add_user_language(self, user_id: int, language_data: UserLanguageCreate) -> UserLanguage:
        """
        Ajoute une langue à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            language_data: Données de la langue
            
        Returns:
            Langue créée
        """
        language = UserLanguage(
            user_id=user_id,
            **language_data.dict()
        )
        
        self.db.add(language)
        self.db.commit()
        self.db.refresh(language)
        
        logger.info(f"Langue '{language.language}' ajoutée à l'utilisateur {user_id}")
        return language
    
    def update_user_language(self, language_id: int, language_data: UserLanguageUpdate) -> UserLanguage:
        """
        Met à jour une langue
        
        Args:
            language_id: ID de la langue
            language_data: Données de mise à jour
            
        Returns:
            Langue mise à jour
        """
        language = self.db.query(UserLanguage).filter(UserLanguage.id == language_id).first()
        if not language:
            raise ValueError(f"Langue avec ID {language_id} non trouvée")
        
        update_data = language_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(language, field, value)
        
        self.db.commit()
        self.db.refresh(language)
        
        logger.info(f"Langue {language_id} mise à jour")
        return language
    
    def delete_user_language(self, language_id: int) -> bool:
        """
        Supprime une langue
        
        Args:
            language_id: ID de la langue
            
        Returns:
            True si supprimée avec succès
        """
        language = self.db.query(UserLanguage).filter(UserLanguage.id == language_id).first()
        if not language:
            raise ValueError(f"Langue avec ID {language_id} non trouvée")
        
        self.db.delete(language)
        self.db.commit()
        
        logger.info(f"Langue {language_id} supprimée")
        return True
    
    # Recherche et statistiques
    def search_profiles(self, search_query: ProfileSearchQuery) -> List[Dict[str, Any]]:
        """
        Recherche des profils utilisateurs selon des critères
        
        Args:
            search_query: Critères de recherche
            
        Returns:
            Liste des profils correspondants
        """
        query = self.db.query(User)
        
        # Filtre par compétences
        if search_query.skills:
            query = query.join(User.skills).filter(
                UserSkill.skill_name.in_(search_query.skills)
            )
        
        # Filtre par localisation
        if search_query.location:
            query = query.filter(User.location.ilike(f"%{search_query.location}%"))
        
        # Filtre par entreprise
        if search_query.company:
            query = query.filter(User.company.ilike(f"%{search_query.company}%"))
        
        # Filtre par poste
        if search_query.job_title:
            query = query.filter(User.job_title.ilike(f"%{search_query.job_title}%"))
        
        # Applique la pagination
        users = query.offset(search_query.offset).limit(search_query.limit).all()
        
        # Formate les résultats
        results = []
        for user in users:
            user_skills = [skill.skill_name for skill in user.skills]
            
            results.append({
                "id": user.id,
                "username": user.username,
                "profile_picture": user.profile_picture,
                "job_title": user.job_title,
                "company": user.company,
                "location": user.location,
                "skills": user_skills,
                "match_score": self._calculate_match_score(user, search_query)
            })
        
        return results
    
    def get_profile_stats(self, user_id: int) -> ProfileStatsResponse:
        """
        Récupère les statistiques du profil d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Statistiques du profil
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Utilisateur avec ID {user_id} non trouvé")
        
        # Compte les éléments
        total_skills = len(user.skills)
        total_experiences = len(user.experiences)
        total_educations = len(user.educations)
        total_certifications = self.db.query(UserCertification).filter(
            UserCertification.user_id == user_id
        ).count()
        total_projects = self.db.query(UserProject).filter(
            UserProject.user_id == user_id
        ).count()
        total_languages = self.db.query(UserLanguage).filter(
            UserLanguage.user_id == user_id
        ).count()
        
        # Calcule le pourcentage de complétion
        profile_fields = [
            user.profile_picture, user.biography, user.location,
            user.website, user.company, user.job_title
        ]
        completed_fields = sum(1 for field in profile_fields if field)
        profile_completion_percentage = (completed_fields / len(profile_fields)) * 100
        
        return ProfileStatsResponse(
            total_skills=total_skills,
            total_experiences=total_experiences,
            total_educations=total_educations,
            total_certifications=total_certifications,
            total_projects=total_projects,
            total_languages=total_languages,
            profile_completion_percentage=round(profile_completion_percentage, 2),
            profile_views=0  # À implémenter avec un système de tracking
        )
    
    def _calculate_match_score(self, user: User, search_query: ProfileSearchQuery) -> float:
        """
        Calcule un score de correspondance pour la recherche
        
        Args:
            user: Utilisateur à évaluer
            search_query: Critères de recherche
            
        Returns:
            Score de correspondance (0-100)
        """
        score = 0.0
        max_score = 0.0
        
        # Correspondance des compétences
        if search_query.skills:
            max_score += 40
            user_skills = {skill.skill_name.lower() for skill in user.skills}
            search_skills = {skill.lower() for skill in search_query.skills}
            matching_skills = user_skills.intersection(search_skills)
            if matching_skills:
                skill_match_ratio = len(matching_skills) / len(search_skills)
                score += skill_match_ratio * 40
        
        # Correspondance de la localisation
        if search_query.location:
            max_score += 20
            if user.location and search_query.location.lower() in user.location.lower():
                score += 20
        
        # Correspondance de l'entreprise
        if search_query.company:
            max_score += 20
            if user.company and search_query.company.lower() in user.company.lower():
                score += 20
        
        # Correspondance du poste
        if search_query.job_title:
            max_score += 20
            if user.job_title and search_query.job_title.lower() in user.job_title.lower():
                score += 20
        
        # Normalise le score
        if max_score > 0:
            return (score / max_score) * 100
        
        return 0.0


# Dépendance FastAPI
def get_user_profile_service(db: Session) -> UserProfileService:
    """Dépendance pour obtenir le service de profils utilisateurs"""
    return UserProfileService(db)
