# backend/app/controllers/user_profile_controller.py
"""
Contrôleur pour la gestion des profils utilisateurs avancés
Endpoints pour la photo, biographie, compétences, expériences et formations
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.services.user_profile_service import UserProfileService, get_user_profile_service
from app.schemas.user_profile_schema import (
    UserProfileUpdate, UserProfileResponse, UserProfileCompleteResponse,
    UserSkillCreate, UserSkillResponse, UserSkillUpdate,
    UserExperienceCreate, UserExperienceResponse, UserExperienceUpdate,
    UserEducationCreate, UserEducationResponse, UserEducationUpdate,
    UserCertificationCreate, UserCertificationResponse, UserCertificationUpdate,
    UserProjectCreate, UserProjectResponse, UserProjectUpdate,
    UserLanguageCreate, UserLanguageResponse, UserLanguageUpdate,
    ProfileSearchQuery, ProfileSearchResponse, ProfileStatsResponse,
    SkillBulkCreate, ExperienceBulkCreate, EducationBulkCreate
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


# Gestion du profil principal
@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Mettre à jour le profil",
    description="Met à jour le profil principal de l'utilisateur courant"
)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)  # À implémenter avec l'authentification
):
    """
    Met à jour le profil de l'utilisateur courant
    
    - **profile_picture**: URL de la photo de profil
    - **biography**: Biographie de l'utilisateur
    - **location**: Localisation
    - **website**: Site web personnel
    - **company**: Entreprise
    - **job_title**: Poste
    - **social_links**: Liens sociaux
    - **profile_visibility**: Visibilité du profil
    """
    try:
        # Dans une implémentation réelle, vous obtiendriez l'utilisateur courant
        # user_id = current_user.id
        user_id = 1  # Pour la démonstration
        
        user = profile_service.update_user_profile(user_id, profile_data)
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du profil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour du profil"
        )


@router.get(
    "/me",
    response_model=UserProfileCompleteResponse,
    summary="Récupérer mon profil",
    description="Récupère le profil complet de l'utilisateur courant"
)
async def get_my_profile(
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Récupère le profil complet de l'utilisateur courant
    """
    try:
        user_id = 1  # Pour la démonstration
        
        user = profile_service.get_user_profile(user_id)
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération du profil"
        )


@router.get(
    "/{user_id}",
    response_model=UserProfileCompleteResponse,
    summary="Récupérer un profil utilisateur",
    description="Récupère le profil complet d'un utilisateur spécifique"
)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """
    Récupère le profil complet d'un utilisateur spécifique
    
    - **user_id**: ID de l'utilisateur
    """
    try:
        user = profile_service.get_user_profile(user_id)
        
        # Vérifie la visibilité du profil
        if user.profile_visibility == "private":
            # Dans une implémentation réelle, vérifier les autorisations
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce profil est privé"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération du profil"
        )


@router.post(
    "/me/picture",
    summary="Télécharger une photo de profil",
    description="Télécharge une photo de profil pour l'utilisateur courant"
)
async def upload_profile_picture(
    file: UploadFile = File(..., description="Fichier image (JPG, PNG)"),
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Télécharge une photo de profil
    
    - **file**: Fichier image (JPG, PNG, max 5MB)
    """
    try:
        user_id = 1  # Pour la démonstration
        
        # Vérifie le type de fichier
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type de fichier non supporté. Utilisez JPG ou PNG."
            )
        
        # Lit le contenu du fichier
        file_content = await file.read()
        
        # Vérifie la taille du fichier (max 5MB)
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fichier trop volumineux. Maximum 5MB."
            )
        
        # Télécharge la photo
        profile_url = profile_service.upload_profile_picture(
            user_id, file_content, file.filename
        )
        
        return {"profile_picture_url": profile_url}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la photo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du téléchargement de la photo"
        )


# Gestion des compétences
@router.post(
    "/me/skills",
    response_model=UserSkillResponse,
    summary="Ajouter une compétence",
    description="Ajoute une compétence à l'utilisateur courant"
)
async def add_skill(
    skill_data: UserSkillCreate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Ajoute une compétence
    
    - **skill_name**: Nom de la compétence
    - **skill_level**: Niveau (beginner, intermediate, advanced, expert)
    - **category**: Catégorie de compétence
    - **years_of_experience**: Années d'expérience
    - **is_verified**: Compétence vérifiée
    """
    try:
        user_id = 1  # Pour la démonstration
        
        skill = profile_service.add_user_skill(user_id, skill_data)
        return skill
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la compétence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'ajout de la compétence"
        )


@router.post(
    "/me/skills/bulk",
    response_model=List[UserSkillResponse],
    summary="Ajouter plusieurs compétences",
    description="Ajoute plusieurs compétences en une seule requête"
)
async def add_skills_bulk(
    skills_data: SkillBulkCreate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Ajoute plusieurs compétences
    
    - **skills**: Liste des compétences à ajouter
    """
    try:
        user_id = 1  # Pour la démonstration
        
        skills = []
        for skill_data in skills_data.skills:
            skill = profile_service.add_user_skill(user_id, skill_data)
            skills.append(skill)
        
        return skills
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des compétences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'ajout des compétences"
        )


@router.put(
    "/me/skills/{skill_id}",
    response_model=UserSkillResponse,
    summary="Mettre à jour une compétence",
    description="Met à jour une compétence spécifique"
)
async def update_skill(
    skill_id: int,
    skill_data: UserSkillUpdate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Met à jour une compétence
    
    - **skill_id**: ID de la compétence
    - **skill_level**: Niveau (optionnel)
    - **category**: Catégorie (optionnel)
    - **years_of_experience**: Années d'expérience (optionnel)
    - **is_verified**: Compétence vérifiée (optionnel)
    """
    try:
        skill = profile_service.update_user_skill(skill_id, skill_data)
        return skill
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la compétence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour de la compétence"
        )


@router.delete(
    "/me/skills/{skill_id}",
    summary="Supprimer une compétence",
    description="Supprime une compétence spécifique"
)
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Supprime une compétence
    
    - **skill_id**: ID de la compétence
    """
    try:
        profile_service.delete_user_skill(skill_id)
        return {"message": "Compétence supprimée avec succès"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la compétence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la suppression de la compétence"
        )


@router.get(
    "/me/skills",
    response_model=List[UserSkillResponse],
    summary="Récupérer mes compétences",
    description="Récupère toutes les compétences de l'utilisateur courant"
)
async def get_my_skills(
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les compétences
    """
    try:
        user_id = 1  # Pour la démonstration
        
        skills = profile_service.get_user_skills(user_id)
        return skills
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des compétences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des compétences"
        )


# Gestion des expériences professionnelles
@router.post(
    "/me/experiences",
    response_model=UserExperienceResponse,
    summary="Ajouter une expérience",
    description="Ajoute une expérience professionnelle à l'utilisateur courant"
)
async def add_experience(
    experience_data: UserExperienceCreate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Ajoute une expérience professionnelle
    
    - **company**: Entreprise
    - **job_title**: Poste
    - **description**: Description du poste
    - **location**: Localisation
    - **start_date**: Date de début
    - **end_date**: Date de fin (optionnel)
    - **is_current**: Poste actuel
    - **employment_type**: Type d'emploi
    - **skills_used**: Compétences utilisées
    """
    try:
        user_id = 1  # Pour la démonstration
        
        experience = profile_service.add_user_experience(user_id, experience_data)
        return experience
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de l'expérience: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'ajout de l'expérience"
        )


@router.post(
    "/me/experiences/bulk",
    response_model=List[UserExperienceResponse],
    summary="Ajouter plusieurs expériences",
    description="Ajoute plusieurs expériences en une seule requête"
)
async def add_experiences_bulk(
    experiences_data: ExperienceBulkCreate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Ajoute plusieurs expériences
    
    - **experiences**: Liste des expériences à ajouter
    """
    try:
        user_id = 1  # Pour la démonstration
        
        experiences = []
        for experience_data in experiences_data.experiences:
            experience = profile_service.add_user_experience(user_id, experience_data)
            experiences.append(experience)
        
        return experiences
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des expériences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'ajout des expériences"
        )


@router.put(
    "/me/experiences/{experience_id}",
    response_model=UserExperienceResponse,
    summary="Mettre à jour une expérience",
    description="Met à jour une expérience spécifique"
)
async def update_experience(
    experience_id: int,
    experience_data: UserExperienceUpdate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Met à jour une expérience professionnelle
    
    - **experience_id**: ID de l'expérience
    """
    try:
        experience = profile_service.update_user_experience(experience_id, experience_data)
        return experience
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'expérience: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour de l'expérience"
        )


@router.delete(
    "/me/experiences/{experience_id}",
    summary="Supprimer une expérience",
    description="Supprime une expérience spécifique"
)
async def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Supprime une expérience professionnelle
    
    - **experience_id**: ID de l'expérience
    """
    try:
        profile_service.delete_user_experience(experience_id)
        return {"message": "Expérience supprimée avec succès"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'expérience: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la suppression de l'expérience"
        )


@router.get(
    "/me/experiences",
    response_model=List[UserExperienceResponse],
    summary="Récupérer mes expériences",
    description="Récupère toutes les expériences de l'utilisateur courant"
)
async def get_my_experiences(
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les expériences professionnelles
    """
    try:
        user_id = 1  # Pour la démonstration
        
        experiences = profile_service.get_user_experiences(user_id)
        return experiences
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des expériences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des expériences"
        )


# Gestion des formations
@router.post(
    "/me/educations",
    response_model=UserEducationResponse,
    summary="Ajouter une formation",
    description="Ajoute une formation à l'utilisateur courant"
)
async def add_education(
    education_data: UserEducationCreate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Ajoute une formation
    
    - **institution**: Établissement
    - **degree**: Diplôme
    - **field_of_study**: Domaine d'étude
    - **description**: Description de la formation
    - **start_date**: Date de début
    - **end_date**: Date de fin (optionnel)
    - **is_current**: Formation en cours
    - **grade**: Note/moyenne
    - **activities**: Activités extrascolaires
    """
    try:
        user_id = 1  # Pour la démonstration
        
        education = profile_service.add_user_education(user_id, education_data)
        return education
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la formation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'ajout de la formation"
        )


@router.post(
    "/me/educations/bulk",
    response_model=List[UserEducationResponse],
    summary="Ajouter plusieurs formations",
    description="Ajoute plusieurs formations en une seule requête"
)
async def add_educations_bulk(
    educations_data: EducationBulkCreate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Ajoute plusieurs formations
    
    - **educations**: Liste des formations à ajouter
    """
    try:
        user_id = 1  # Pour la démonstration
        
        educations = []
        for education_data in educations_data.educations:
            education = profile_service.add_user_education(user_id, education_data)
            educations.append(education)
        
        return educations
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des formations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'ajout des formations"
        )


@router.put(
    "/me/educations/{education_id}",
    response_model=UserEducationResponse,
    summary="Mettre à jour une formation",
    description="Met à jour une formation spécifique"
)
async def update_education(
    education_id: int,
    education_data: UserEducationUpdate,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Met à jour une formation
    
    - **education_id**: ID de la formation
    """
    try:
        education = profile_service.update_user_education(education_id, education_data)
        return education
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la formation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour de la formation"
        )


@router.delete(
    "/me/educations/{education_id}",
    summary="Supprimer une formation",
    description="Supprime une formation spécifique"
)
async def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Supprime une formation
    
    - **education_id**: ID de la formation
    """
    try:
        profile_service.delete_user_education(education_id)
        return {"message": "Formation supprimée avec succès"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la formation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la suppression de la formation"
        )


@router.get(
    "/me/educations",
    response_model=List[UserEducationResponse],
    summary="Récupérer mes formations",
    description="Récupère toutes les formations de l'utilisateur courant"
)
async def get_my_educations(
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les formations
    """
    try:
        user_id = 1  # Pour la démonstration
        
        educations = profile_service.get_user_educations(user_id)
        return educations
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des formations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des formations"
        )


# Recherche et statistiques
@router.post(
    "/search",
    response_model=List[ProfileSearchResponse],
    summary="Rechercher des profils",
    description="Recherche des profils utilisateurs selon des critères"
)
async def search_profiles(
    search_query: ProfileSearchQuery,
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """
    Recherche des profils utilisateurs
    
    - **skills**: Compétences recherchées
    - **location**: Localisation
    - **company**: Entreprise
    - **job_title**: Poste
    - **min_experience**: Expérience minimale en années
    - **limit**: Nombre maximum de résultats
    - **offset**: Décalage pour la pagination
    """
    try:
        results = profile_service.search_profiles(search_query)
        return results
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de profils: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la recherche de profils"
        )


@router.get(
    "/me/stats",
    response_model=ProfileStatsResponse,
    summary="Statistiques du profil",
    description="Récupère les statistiques du profil de l'utilisateur courant"
)
async def get_my_profile_stats(
    db: Session = Depends(get_db),
    profile_service: UserProfileService = Depends(get_user_profile_service)
    # current_user: User = Depends(get_current_user)
):
    """
    Récupère les statistiques du profil
    """
    try:
        user_id = 1  # Pour la démonstration
        
        stats = profile_service.get_profile_stats(user_id)
        return stats
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des statistiques"
        )


# Endpoint de santé
@router.get("/health")
async def profile_health_check(
    profile_service: UserProfileService = Depends(get_user_profile_service)
) -> dict:
    """
    Vérification de santé du service de profils
    """
    try:
        # Test simple de fonctionnement
        user_id = 1
        try:
            profile_service.get_user_profile(user_id)
        except ValueError:
            # C'est normal si l'utilisateur de test n'existe pas
            pass
        
        return {"status": "healthy", "service": "user_profile_service"}
        
    except Exception as e:
        logger.error(f"Erreur de santé du service de profils: {str(e)}")
        return {"status": "unhealthy", "service": "user_profile_service", "error": str(e)}
