# Documentation - Profils Utilisateurs Avancés

## Table des Matières
1. [Aperçu du Système](#aperçu-du-système)
2. [Architecture Technique](#architecture-technique)
3. [Modèles de Données](#modèles-de-données)
4. [API Endpoints](#api-endpoints)
5. [Gestion des Photos](#gestion-des-photos)
6. [Recherche et Filtrage](#recherche-et-filtrage)
7. [Statistiques et Métriques](#statistiques-et-métriques)
8. [Intégration Frontend](#intégration-frontend)
9. [Sécurité et Confidentialité](#sécurité-et-confidentialité)

## Aperçu du Système

Le système de profils utilisateurs avancés permet aux utilisateurs de créer des profils détaillés incluant photo, biographie, compétences, expériences professionnelles, formations et projets personnels.

### Fonctionnalités Principales

- ✅ **Profil principal** : Photo, biographie, localisation, informations professionnelles
- ✅ **Compétences** : Gestion des compétences avec niveaux et catégories
- ✅ **Expériences professionnelles** : Historique d'emploi avec descriptions détaillées
- ✅ **Formations** : Éducation et certifications
- ✅ **Projets personnels** : Portfolio de projets avec technologies utilisées
- ✅ **Langues** : Gestion des langues parlées avec niveaux de maîtrise
- ✅ **Recherche avancée** : Recherche de profils par compétences et critères
- ✅ **Statistiques** : Métriques de complétion et d'engagement

## Architecture Technique

### Composants du Système

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Contrôleur    │◄──►│  Profile Service │◄──►│  Base de       │
│     Profils     │    │                  │    │  Données       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│     Schémas     │    │     Modèles      │
│    Pydantic     │    │      SQLAlchemy  │
└─────────────────┘    └──────────────────┘
```

### Fichiers Implémentés

- [`backend/app/models/user.py`](backend/app/models/user.py) - Extension du modèle utilisateur principal
- [`backend/app/models/user_profile.py`](backend/app/models/user_profile.py) - Modèles pour les profils avancés
- [`backend/app/schemas/user_profile_schema.py`](backend/app/schemas/user_profile_schema.py) - Schémas Pydantic pour la validation
- [`backend/app/services/user_profile_service.py`](backend/app/services/user_profile_service.py) - Service de gestion des profils
- [`backend/app/controllers/user_profile_controller.py`](backend/app/controllers/user_profile_controller.py) - Endpoints API pour les profils

## Modèles de Données

### Utilisateur Principal (Étendu)

```python
class User(Base):
    # Champs existants
    username, email, hashed_password, age, can_be_contacted, can_data_be_shared
    
    # Nouveaux champs pour le profil avancé
    profile_picture = Column(String)      # URL de la photo
    biography = Column(Text)              # Biographie
    location = Column(String)             # Localisation
    website = Column(String)              # Site web
    company = Column(String)              # Entreprise
    job_title = Column(String)            # Poste
    social_links = Column(JSON)           # Liens sociaux
    profile_visibility = Column(String)   # Visibilité (public/private/contacts_only)
    profile_updated_at = Column(DateTime) # Date de mise à jour
```

### Compétences (UserSkill)

```python
class UserSkill(Base):
    skill_name = Column(String(100))      # Nom de la compétence
    skill_level = Column(String(20))      # Niveau (beginner, intermediate, advanced, expert)
    category = Column(String(50))         # Catégorie
    years_of_experience = Column(Float)   # Années d'expérience
    is_verified = Column(Boolean)         # Compétence vérifiée
    verified_by = Column(Integer)         # Qui a vérifié
```

### Expériences Professionnelles (UserExperience)

```python
class UserExperience(Base):
    company = Column(String(200))         # Entreprise
    job_title = Column(String(200))       # Poste
    description = Column(Text)            # Description
    location = Column(String(100))        # Localisation
    start_date = Column(DateTime)         # Date de début
    end_date = Column(DateTime)           # Date de fin
    is_current = Column(Boolean)          # Poste actuel
    employment_type = Column(String(50))  # Type d'emploi
    skills_used = Column(JSON)            # Compétences utilisées
```

### Formations (UserEducation)

```python
class UserEducation(Base):
    institution = Column(String(200))     # Établissement
    degree = Column(String(200))          # Diplôme
    field_of_study = Column(String(200))  # Domaine d'étude
    description = Column(Text)            # Description
    start_date = Column(DateTime)         # Date de début
    end_date = Column(DateTime)           # Date de fin
    is_current = Column(Boolean)          # Formation en cours
    grade = Column(String(50))            # Note/moyenne
    activities = Column(Text)             # Activités extrascolaires
```

## API Endpoints

### Gestion du Profil Principal

#### PUT /api/profiles/me
Met à jour le profil principal de l'utilisateur courant.

**Body:**
```json
{
    "profile_picture": "string (optionnel)",
    "biography": "string (optionnel)",
    "location": "string (optionnel)",
    "website": "string (optionnel)",
    "company": "string (optionnel)",
    "job_title": "string (optionnel)",
    "social_links": {
        "linkedin": "https://linkedin.com/in/username",
        "github": "https://github.com/username",
        "twitter": "https://twitter.com/username"
    },
    "profile_visibility": "public"
}
```

#### GET /api/profiles/me
Récupère le profil complet de l'utilisateur courant.

#### GET /api/profiles/{user_id}
Récupère le profil complet d'un utilisateur spécifique.

#### POST /api/profiles/me/picture
Télécharge une photo de profil.

**Form Data:**
- `file`: Fichier image (JPG, PNG, max 5MB)

### Gestion des Compétences

#### POST /api/profiles/me/skills
Ajoute une compétence.

**Body:**
```json
{
    "skill_name": "Python",
    "skill_level": "advanced",
    "category": "programming",
    "years_of_experience": 5,
    "is_verified": false
}
```

#### POST /api/profiles/me/skills/bulk
Ajoute plusieurs compétences en une seule requête.

**Body:**
```json
{
    "skills": [
        {
            "skill_name": "Python",
            "skill_level": "advanced",
            "category": "programming"
        },
        {
            "skill_name": "FastAPI",
            "skill_level": "intermediate",
            "category": "framework"
        }
    ]
}
```

#### PUT /api/profiles/me/skills/{skill_id}
Met à jour une compétence spécifique.

#### DELETE /api/profiles/me/skills/{skill_id}
Supprime une compétence.

#### GET /api/profiles/me/skills
Récupère toutes les compétences de l'utilisateur.

### Gestion des Expériences Professionnelles

#### POST /api/profiles/me/experiences
Ajoute une expérience professionnelle.

**Body:**
```json
{
    "company": "Tech Corp",
    "job_title": "Senior Developer",
    "description": "Développement d'applications web...",
    "location": "Paris, France",
    "start_date": "2020-01-01T00:00:00",
    "end_date": "2023-12-31T23:59:59",
    "is_current": false,
    "employment_type": "full_time",
    "skills_used": ["Python", "FastAPI", "PostgreSQL"]
}
```

#### POST /api/profiles/me/experiences/bulk
Ajoute plusieurs expériences en une seule requête.

#### PUT /api/profiles/me/experiences/{experience_id}
Met à jour une expérience.

#### DELETE /api/profiles/me/experiences/{experience_id}
Supprime une expérience.

#### GET /api/profiles/me/experiences
Récupère toutes les expériences de l'utilisateur.

### Gestion des Formations

#### POST /api/profiles/me/educations
Ajoute une formation.

**Body:**
```json
{
    "institution": "Université Paris-Saclay",
    "degree": "Master Informatique",
    "field_of_study": "Informatique",
    "description": "Spécialisation en développement web...",
    "start_date": "2015-09-01T00:00:00",
    "end_date": "2020-06-30T23:59:59",
    "is_current": false,
    "grade": "Mention Bien",
    "activities": "Président du club informatique"
}
```

#### POST /api/profiles/me/educations/bulk
Ajoute plusieurs formations en une seule requête.

#### PUT /api/profiles/me/educations/{education_id}
Met à jour une formation.

#### DELETE /api/profiles/me/educations/{education_id}
Supprime une formation.

#### GET /api/profiles/me/educations
Récupère toutes les formations de l'utilisateur.

### Recherche et Statistiques

#### POST /api/profiles/search
Recherche des profils selon des critères.

**Body:**
```json
{
    "skills": ["Python", "FastAPI"],
    "location": "Paris",
    "company": "Tech Corp",
    "job_title": "Developer",
    "min_experience": 3,
    "limit": 20,
    "offset": 0
}
```

#### GET /api/profiles/me/stats
Récupère les statistiques du profil.

**Réponse:**
```json
{
    "total_skills": 8,
    "total_experiences": 3,
    "total_educations": 2,
    "total_certifications": 1,
    "total_projects": 5,
    "total_languages": 2,
    "profile_completion_percentage": 85.5,
    "profile_views": 124
}
```

## Gestion des Photos

### Processus de Téléchargement

1. **Validation** : Vérification du type et de la taille du fichier
2. **Génération de nom unique** : `profile_{user_id}_{uuid}.{extension}`
3. **Stockage** : Sauvegarde dans le dossier `uploads/profiles/`
4. **Mise à jour du profil** : Mise à jour de l'URL de la photo

### Restrictions

- **Types supportés** : JPG, JPEG, PNG
- **Taille maximale** : 5MB
- **Stockage** : Système de fichiers local (peut être adapté pour le cloud)

## Recherche et Filtrage

### Algorithme de Recherche

Le système utilise un algorithme de scoring pour classer les résultats :

```python
def _calculate_match_score(user, search_query):
    score = 0.0
    max_score = 0.0
    
    # Correspondance des compétences (40%)
    if search_query.skills:
        max_score += 40
        user_skills = {skill.skill_name.lower() for skill in user.skills}
        search_skills = {skill.lower() for skill in search_query.skills}
        matching_skills = user_skills.intersection(search_skills)
        if matching_skills:
            skill_match_ratio = len(matching_skills) / len(search_skills)
            score += skill_match_ratio * 40
    
    # Correspondance de la localisation (20%)
    if search_query.location:
        max_score += 20
        if user.location and search_query.location.lower() in user.location.lower():
            score += 20
    
    # Correspondance de l'entreprise (20%)
    if search_query.company:
        max_score += 20
        if user.company and search_query.company.lower() in user.company.lower():
            score += 20
    
    # Correspondance du poste (20%)
    if search_query.job_title:
        max_score += 20
        if user.job_title and search_query.job_title.lower() in user.job_title.lower():
            score += 20
    
    # Normalisation
    if max_score > 0:
        return (score / max_score) * 100
    
    return 0.0
```

### Critères de Recherche

- **Compétences** : Recherche par nom de compétence
- **Localisation** : Recherche textuelle dans le champ location
- **Entreprise** : Recherche dans l'historique professionnel
- **Poste** : Recherche dans les titres de poste
- **Expérience minimale** : Filtrage par années d'expérience

## Statistiques et Métriques

### Calcul de Complétion du Profil

```python
profile_fields = [
    user.profile_picture, user.biography, user.location,
    user.website, user.company, user.job_title
]
completed_fields = sum(1 for field in profile_fields if field)
profile_completion_percentage = (completed_fields / len(profile_fields)) * 100
```

### Métriques Disponibles

- **Compétences** : Nombre total de compétences
- **Expériences** : Nombre d'expériences professionnelles
- **Formations** : Nombre de formations
- **Certifications** : Nombre de certifications
- **Projets** : Nombre de projets personnels
- **Langues** : Nombre de langues parlées
- **Complétion** : Pourcentage de complétion du profil
- **Vues** : Nombre de vues du profil (à implémenter)

## Intégration Frontend

### Exemple d'Intégration avec React

```javascript
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

const UserProfile = () => {
    const { user } = useAuth();
    const [profile, setProfile] = useState(null);
    const [skills, setSkills] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUserProfile();
    }, []);

    const fetchUserProfile = async () => {
        try {
            const response = await fetch('/api/profiles/me', {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            const profileData = await response.json();
            setProfile(profileData);
            setSkills(profileData.skills);
        } catch (error) {
            console.error('Erreur lors du chargement du profil:', error);
        } finally {
            setLoading(false);
        }
    };

    const addSkill = async (skillData) => {
        try {
            const response = await fetch('/api/profiles/me/skills', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(skillData)
            });
            const newSkill = await response.json();
            setSkills([...skills, newSkill]);
        } catch (error) {
            console.error('Erreur lors de l\'ajout de la compétence:', error);
        }
    };

    if (loading) return <div>Chargement du profil...</div>;

    return (
        <div className="profile-container">
            <div className="profile-header">
                <img 
                    src={profile.profile_picture || '/default-avatar.png'} 
                    alt="Photo de profil"
                    className="profile-picture"
                />
                <div className="profile-info">
                    <h1>{profile.username}</h1>
                    <p className="job-title">{profile.job_title}</p>
                    <p className="company">{profile.company}</p>
                    <p className="location">{profile.location}</p>
                </div>
            </div>
            
            <div className="profile-section">
                <h2>Biographie</h2>
                <p>{profile.biography || 'Aucune biographie renseignée'}</p>
            </div>
            
            <div className="profile-section">
                <h2>Compétences</h2>
                <div className="skills-list">
                    {skills.map(skill => (
                        <div key={skill.id} className="skill-item">
                            <span className="skill-name">{skill.skill_name}</span>
                            <span className={`skill-level ${skill.skill_level}`}>
                                {skill.skill_level}
                            </span>
                        </div>
                    ))}
                </div>
                <button onClick={() => addSkill({ skill_name: 'Nouvelle compétence', skill_level: 'beginner' })}>
                    Ajouter une compétence
                </button>
            </div>
        </div>
    );
};

export default UserProfile;
```

### Upload de Photo de Profil

```javascript
const uploadProfilePicture = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/profiles/me/picture', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${user.token}`
            },
            body: formData
        });
        
        const result = await response.json();
        setProfile(prev => ({ ...prev, profile_picture: result.profile_picture_url }));
        
    } catch (error) {
        console.error('Erreur lors du téléchargement de la photo:', error);
    }
};
```

## Sécurité et Confidentialité

### Visibilité des Profils

Le système supporte trois niveaux de visibilité :

- **Public** : Profil visible par tous les utilisateurs
- **Contacts uniquement** : Profil visible uniquement par les contacts approuvés
- **Privé** : Profil visible uniquement par l'utilisateur

### Contrôles d'Accès

- **Authentification requise** pour les opérations de modification
- **Vérification des permissions** pour l'accès aux profils privés
- **Validation des données** avec schémas Pydantic
- **Limitation des fichiers** pour les uploads de photos

### Bonnes Pratiques

1. **Validation côté serveur** : Toujours valider les données côté serveur
2. **Sanitisation** : Nettoyer les entrées utilisateur pour prévenir les injections
3. **Limitation de taille** : Limiter la taille des fichiers uploadés
4. **Contrôle d'accès** : Vérifier les permissions pour chaque opération
5. **Journalisation** : Logger les opérations sensibles

## Configuration et Déploiement

### Variables d'Environnement

```python
# Configuration des uploads
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FILE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
UPLOAD_DIR = "uploads/profiles"

# Configuration de la base de données
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Configuration de sécurité
PROFILE_VISIBILITY_DEFAULT = "public"
MAX_SKILLS_PER_USER = 50
```

### Migration de Base de Données

Pour déployer le système, exécutez les migrations :

```bash
# Générer les migrations
alembic revision --autogenerate -m "Add advanced user profiles"

# Appliquer les migrations
alembic upgrade head
```

## Tests et Monitoring

### Tests Unitaires

```python
def test_profile_creation():
    """Test la création d'un profil utilisateur"""
    user = create_test_user()
    profile_data = UserProfileUpdate(
        biography="Développeur passionné",
        location="Paris, France",
        job_title="Senior Developer"
    )
    
    updated_user = profile_service.update_user_profile(user.id, profile_data)
    
    assert updated_user.biography == "Développeur passionné"
    assert updated_user.location == "Paris, France"
    assert updated_user.job_title == "Senior Developer"

def test_skill_management():
    """Test la gestion des compétences"""
    user = create_test_user()
    skill_data = UserSkillCreate(
        skill_name="Python",
        skill_level="advanced",
        category="programming"
    )
    
    skill = profile_service.add_user_skill(user.id, skill_data)
    
    assert skill.skill_name == "Python"
    assert skill.skill_level == "advanced"
    assert skill.user_id == user.id
```

### Métriques de Performance

- **Temps de réponse** : Temps moyen des requêtes API
- **Taux d'utilisation** : Nombre de profils créés et mis à jour
- **Complétion moyenne** : Pourcentage moyen de complétion des profils
- **Recherches** : Nombre et efficacité des recherches de profils

## Conclusion

Le système de profils utilisateurs avancés fournit une solution complète pour :

- ✅ **Gestion détaillée** des informations utilisateur
- ✅ **Portfolio professionnel** avec compétences et expériences
- ✅ **Recherche avancée** pour découvrir des talents
- ✅ **Statistiques et insights** sur l'engagement utilisateur
- ✅ **Sécurité et confidentialité** avec contrôles granulaires

Ce système s'intègre parfaitement avec l'infrastructure existante RBAC, OAuth2, et gestion des sessions pour offrir une expérience utilisateur riche et sécurisée.