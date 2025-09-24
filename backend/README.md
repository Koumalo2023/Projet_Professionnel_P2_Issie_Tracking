# SoftDesk - API de Gestion de Projets Collaboratifs

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

## 📝 Description

SoftDesk est une **API RESTful sécurisée** pour la gestion collaborative de projets de développement logiciel. Elle permet aux équipes de :

- 🗂 Organiser des projets avec suivi des problèmes
- 👥 Gérer les contributeurs et permissions
- 💬 Collaborer via un système de commentaires
- 🔒 Respecter les normes RGPD et sécurité OWASP

## ✨ Fonctionnalités

### 🛠 Core Features
- **Authentification JWT** sécurisée
- **Gestion des projets** (création, modification, suppression)
- **Suivi des problèmes** (issues) avec tags et priorités
- **Système de commentaires**
- **Pagination** intelligente
- **Green Code** optimisé

### 🔐 Sécurité
- Validation des données avec Pydantic
- Protection contre les attaques par force brute
- Conformité RGPD (droit à l'oubli, consentement)
- HTTPS recommandé en production

## 🚀 Installation

### Prérequis
- Python 3.9+
- PostgreSQL
- Pipenv (recommandé)

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-repo/softdesk-api.git
cd softdesk-api

# 2. Configurer l'environnement
cp .env.example .env
# Editer les variables dans .env

# 3. Installer les dépendances
pipenv install
pipenv shell

# 4. Lancer l'application
uvicorn app.main:app --reload

## 🚀 Installation
📚 Documentation API
La documentation interactive est disponible via :

Swagger UI: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc



🤝 Contribution
Forkez le projet

Créez une branche (git checkout -b feature/AmazingFeature)

Committez vos changements (git commit -m 'Add some AmazingFeature')

Pushez (git push origin feature/AmazingFeature)

Ouvrez une Pull Request

📄 Licence
Distribué sous licence MIT. Voir LICENSE pour plus d'informations.

✉️ Contact
Votre Nom - @votre_twitter - votre.email@example.com

Project Link: https://github.com/votre-repo/softdesk-api