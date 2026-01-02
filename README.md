# Projet Professionnel P2 - Issie Tracking

Un système de suivi de problèmes (issue tracking) moderne avec backend FastAPI, offrant des fonctionnalités avancées d'authentification et de gestion des autorisations.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Technologies utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Contribuer](#contribuer)
- [Licence](#licence)

## 🎯 Aperçu

Issie Tracking est une plateforme de gestion de projets et de suivi de problèmes conçue pour les équipes de développement. Elle permet de créer des projets, d'ajouter des problèmes (issues), d'assigner des contributeurs, de suivre l'état des tâches et de collaborer via des commentaires.

Le système intègre des mécanismes de sécurité avancés incluant l'authentification OAuth2, RBAC (Role-Based Access Control), MFA (Multi-Factor Authentication) et une gestion fine des permissions.

## ✨ Fonctionnalités

### 🔐 Authentification & Sécurité
- **OAuth2 avec JWT** : Authentification sécurisée avec tokens d'accès et de rafraîchissement
- **RBAC (Role-Based Access Control)** : Système de rôles (Admin, Project Manager, Developer, Viewer) avec permissions granulaires
- **MFA (Multi-Factor Authentication)** : Support de l'authentification à deux facteurs via TOTP
- **Gestion des sessions** : Sessions utilisateur avec expiration et révocation
- **Validation des tokens** : Vérification JWT avec signature HMAC

### 📊 Gestion de Projets
- Création et gestion de projets avec métadonnées
- Invitation de contributeurs aux projets
- Rôles par projet (Owner, Manager, Developer, Viewer)
- Tableau de bord de projet avec statistiques

### 🐛 Suivi des Issues
- Création, modification, suppression d'issues
- États personnalisables (Open, In Progress, Review, Closed)
- Priorités (Low, Medium, High, Critical)
- Étiquettes (labels) et catégories
- Historique des modifications

### 👥 Collaboration
- Système de commentaires sur les issues
- Mentions d'utilisateurs
- Notifications (à venir)
- Activité récente

### 🔧 Administration
- Interface d'administration pour la gestion des utilisateurs
- Audit des actions utilisateur
- Configuration système
- Gestion des rôles et permissions

## 🏗️ Architecture

Le projet suit une architecture hexagonale (ports & adapters) avec séparation claire des responsabilités :

```
backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── auth/               # Logique d'authentification
│   ├── controllers/        # Contrôleurs API
│   ├── services/          # Logique métier
│   ├── repositories/      # Accès aux données
│   ├── models/           # Modèles SQLAlchemy
│   ├── schemas/          # Schémas Pydantic
│   ├── exceptions/       # Exceptions personnalisées
│   ├── middleware/       # Middleware FastAPI
│   └── utils/            # Utilitaires
├── alembic/              # Migrations de base de données
└── tests/                # Tests unitaires et d'intégration
```

## 🛠️ Technologies utilisées

### Backend
- **FastAPI** : Framework web moderne et rapide
- **SQLAlchemy** : ORM pour la gestion de la base de données
- **PostgreSQL** : Base de données relationnelle
- **Alembic** : Gestion des migrations de base de données
- **Pydantic** : Validation des données et schémas
- **Python-JOSE** : Génération et validation de JWT
- **Passlib** : Hachage de mots de passe

### Sécurité
- **OAuth2** avec flux Password et Refresh Token
- **JWT** (JSON Web Tokens) pour l'authentification stateless
- **TOTP** pour l'authentification à deux facteurs
- **RBAC** avec permissions hiérarchiques

### Outils de développement
- **Pytest** : Framework de tests
- **Black & Flake8** : Formatage et linting
- **Docker** : Conteneurisation
- **GitHub Actions** : CI/CD

## 📦 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 14+
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Koumalo2023/Projet_Professionnel_P2_Issie_Tracking.git
   cd Projet_Professionnel_P2_Issie_Tracking/backend
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   ```bash
   # Créer une base de données PostgreSQL
   createdb issie_tracking
   
   # Configurer les variables d'environnement
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

5. **Exécuter les migrations**
   ```bash
   alembic upgrade head
   ```

6. **Lancer le serveur de développement**
   ```bash
   uvicorn app.main:app --reload
   ```

### Installation avec Docker
```bash
docker-compose up -d
```

## ⚙️ Configuration

Les variables d'environnement suivantes sont requises :

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/issie_tracking

# Security
SECRET_KEY=votre_clé_secrète_très_longue_et_complexe
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2
OAUTH2_CLIENT_ID=votre_client_id
OAUTH2_CLIENT_SECRET=votre_client_secret

# Application
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:4200
```

## 🚀 Utilisation

### Démarrage rapide

1. **Créer un compte administrateur**
   ```bash
   python scripts/create_admin.py
   ```

2. **Accéder à l'interface Swagger**
   Ouvrez votre navigateur à l'adresse : `http://localhost:8000/docs`

3. **Authentification**
   - Utilisez l'endpoint `/auth/login` pour obtenir un token
   - Cliquez sur le bouton "Authorize" dans Swagger et entrez votre token

4. **Créer votre premier projet**
   ```bash
   POST /projects/
   {
     "name": "Mon Premier Projet",
     "description": "Description du projet"
   }
   ```

### Commandes utiles

```bash
# Lancer les tests
pytest

# Exécuter les migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Formater le code
black app/
flake8 app/

# Générer la documentation OpenAPI
python scripts/generate_openapi.py
```

## 📚 API Documentation

L'API est documentée automatiquement avec OpenAPI (Swagger). Accédez aux documentations :

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`
- **OpenAPI JSON** : `http://localhost:8000/openapi.json`

### Endpoints principaux

#### Authentification
- `POST /auth/login` - Connexion utilisateur
- `POST /auth/register` - Inscription
- `POST /auth/refresh` - Rafraîchir le token
- `POST /auth/logout` - Déconnexion
- `POST /auth/mfa/enable` - Activer MFA
- `POST /auth/mfa/verify` - Vérifier MFA

#### Utilisateurs
- `GET /users/me` - Profil de l'utilisateur connecté
- `PUT /users/me` - Mettre à jour le profil
- `GET /users/` - Liste des utilisateurs (admin)
- `GET /users/{user_id}` - Détails d'un utilisateur

#### Projets
- `GET /projects/` - Liste des projets
- `POST /projects/` - Créer un projet
- `GET /projects/{project_id}` - Détails d'un projet
- `PUT /projects/{project_id}` - Mettre à jour un projet
- `DELETE /projects/{project_id}` - Supprimer un projet
- `POST /projects/{project_id}/contributors` - Ajouter un contributeur

#### Issues
- `GET /projects/{project_id}/issues` - Liste des issues
- `POST /projects/{project_id}/issues` - Créer une issue
- `GET /issues/{issue_id}` - Détails d'une issue
- `PUT /issues/{issue_id}` - Mettre à jour une issue
- `DELETE /issues/{issue_id}` - Supprimer une issue
- `POST /issues/{issue_id}/comments` - Ajouter un commentaire

## 🧪 Tests

Le projet inclut une suite de tests complète :

```bash
# Exécuter tous les tests
pytest

# Exécuter les tests avec couverture
pytest --cov=app --cov-report=html

# Exécuter les tests d'intégration
pytest tests/integration/

# Exécuter les tests de performance
pytest tests/performance/
```

### Types de tests
- **Tests unitaires** : Logique métier, services, utilitaires
- **Tests d'intégration** : Contrôleurs, base de données
- **Tests d'authentification** : RBAC, OAuth2, MFA
- **Tests de sécurité** : Validation des tokens, permissions

## 🚢 Déploiement

### Déploiement avec Docker

1. **Construire l'image**
   ```bash
   docker build -t issie-tracking-backend .
   ```

2. **Exécuter le conteneur**
   ```bash
   docker run -p 8000:8000 --env-file .env issie-tracking-backend
   ```

### Déploiement avec Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Déploiement sur Kubernetes
Des fichiers de configuration Kubernetes sont disponibles dans le dossier `k8s/`.

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le projet
2. **Créer une branche** pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalité`)
3. **Commiter** vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. **Pousser** vers la branche (`git push origin feature/ma-fonctionnalité`)
5. **Ouvrir une Pull Request**

### Standards de code
- Suivre les conventions PEP 8
- Écrire des tests pour les nouvelles fonctionnalités
- Documenter les nouvelles APIs
- Mettre à jour le CHANGELOG.md

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une [issue](https://github.com/Koumalo2023/Projet_Professionnel_P2_Issie_Tracking/issues)
- Consulter la [documentation](https://github.com/Koumalo2023/Projet_Professionnel_P2_Issie_Tracking/wiki)

## 🙏 Remerciements

- L'équipe FastAPI pour l'excellent framework
- La communauté PostgreSQL
- Tous les contributeurs open source dont les projets ont été utilisés

---

**Développé avec ❤️ par l'équipe Issie Tracking**