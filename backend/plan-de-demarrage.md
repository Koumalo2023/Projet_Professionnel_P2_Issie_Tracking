# Plan de Démarrage du Backend SoftDesk

## Analyse des Dépendances Identifiées

D'après l'analyse du code, les dépendances Python suivantes sont nécessaires :

### Dépendances Principales
- **FastAPI** - Framework web principal
- **SQLAlchemy** - ORM pour PostgreSQL
- **psycopg2** - Driver PostgreSQL
- **alembic** - Gestion des migrations de base de données
- **python-dotenv** - Gestion des variables d'environnement
- **python-jose** - Gestion des tokens JWT
- **passlib** - Hashage des mots de passe
- **pydantic** - Validation des données

### Dépendances de Développement
- **uvicorn** - Serveur ASGI pour FastAPI

## Fichier Requirements.txt Nécessaire

```txt
fastapi==0.104.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-dotenv==1.0.0
python-jose==3.3.0
passlib==1.7.4
pydantic==2.5.0
uvicorn==0.24.0
```

## Configuration de la Base de Données

La configuration actuelle dans [`database.py`](backend/app/database/database.py:6) utilise :
- **URL de connexion** : `postgresql+psycopg2://postgres:Tefong006@localhost:5432/issue_tracking_db`
- **Base de données** : `issue_tracking_db`

## Étapes de Démarrage

### 1. Vérification de PostgreSQL
```bash
# Vérifier si PostgreSQL est installé
psql --version

# Vérifier si le service PostgreSQL est en cours d'exécution
sudo systemctl status postgresql

# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données si elle n'existe pas
CREATE DATABASE issue_tracking_db;
```

### 2. Configuration de l'Environnement
```bash
# Se déplacer dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Exécution des Migrations
```bash
# Initialiser Alembic (si pas déjà fait)
alembic init alembic

# Exécuter les migrations
alembic upgrade head
```

### 4. Démarrage du Serveur
```bash
# Démarrer le serveur FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints API Disponibles

D'après [`main.py`](backend/app/main.py:30-35), les endpoints suivants seront disponibles :

- **Authentification** : `/api/auth/*`
- **Utilisateurs** : `/users/*`
- **Projets** : `/projects/*`
- **Issues** : `/issues/*`
- **Commentaires** : `/comments/*`
- **Contributeurs** : `/contributors/*`

## Documentation API

Une fois le serveur démarré, la documentation interactive sera disponible :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## Vérifications de Sécurité

### Points à Vérifier
- [ ] Les mots de passe sont hashés avec bcrypt
- [ ] Les tokens JWT ont une durée de vie appropriée
- [ ] La connexion à la base de données utilise SSL en production
- [ ] Les variables sensibles sont dans un fichier .env

### Configuration de Production Recommandée
```python
# Variables d'environnement recommandées
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=votre_secret_key_super_securisee
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Diagramme d'Architecture

```mermaid
graph TD
    A[Client Frontend] --> B[API FastAPI]
    B --> C[Base de Données PostgreSQL]
    B --> D[Authentification JWT]
    B --> E[Services Métier]
    E --> F[Repository Pattern]
    F --> C
    D --> G[Middleware Sécurité]
    G --> B
```

## Prochaines Étapes

1. **Créer le fichier requirements.txt** avec les dépendances identifiées
2. **Configurer PostgreSQL** et créer la base de données
3. **Installer les dépendances** dans un environnement virtuel
4. **Exécuter les migrations** Alembic
5. **Démarrer le serveur** et tester les endpoints

Le backend est prêt à être démarré une fois ces étapes complétées.