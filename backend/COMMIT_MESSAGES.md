# Messages de Commit pour le Projet SoftDesk Backend

## Convention de Commits
Utilisez le format conventionnel suivant : `type(scope): description`

### Types de commits
- **feat**: Nouvelle fonctionnalité
- **fix**: Correction de bug
- **docs**: Documentation
- **style**: Changements de formatage (espaces, virgules, etc.)
- **refactor**: Refactorisation du code
- **test**: Ajout ou modification de tests
- **chore**: Tâches de maintenance, dépendances, etc.

## Messages de Commit Recommandés

### Configuration Initiale
```bash
git commit -m "chore: initialiser la configuration du projet FastAPI"
git commit -m "chore: ajouter les dépendances Python dans requirements.txt"
git commit -m "chore: configurer l'environnement virtuel et les variables d'environnement"
git commit -m "chore: ajouter le fichier .gitignore pour FastAPI"
```

### Infrastructure
```bash
git commit -m "feat(database): configurer la connexion PostgreSQL avec SQLAlchemy"
git commit -m "feat(auth): implémenter l'authentification JWT"
git commit -m "feat(middleware): ajouter le middleware de logging des requêtes"
```

### Modèles de Données
```bash
git commit -m "feat(models): créer les modèles User, Project, Issue"
git commit -m "feat(models): ajouter les modèles Comment et Contributor"
git commit -m "feat(migrations): créer les migrations Alembic initiales"
```

### API Endpoints
```bash
git commit -m "feat(auth): implémenter les endpoints d'authentification"
git commit -m "feat(users): créer le CRUD complet pour les utilisateurs"
git commit -m "feat(projects): implémenter la gestion des projets"
git commit -m "feat(issues): ajouter le système de suivi des problèmes"
git commit -m "feat(comments): implémenter le système de commentaires"
```

### Documentation
```bash
git commit -m "docs(api): ajouter la documentation Swagger/OpenAPI"
git commit -m "docs(readme): mettre à jour le README avec les instructions d'installation"
git commit -m "docs(architecture): documenter l'architecture du projet"
```

### Sécurité et Validation
```bash
git commit -m "feat(security): implémenter la validation des données avec Pydantic"
git commit -m "feat(permissions): ajouter le système de permissions granulaires"
git commit -m "fix(security): corriger les vulnérabilités identifiées"
```

### Exemples de Commits pour les Changements Réalisés

```bash
# Pour les fichiers créés aujourd'hui
git commit -m "chore: créer le fichier requirements.txt avec les dépendances FastAPI"
git commit -m "chore: ajouter le fichier .env pour la configuration JWT"
git commit -m "chore: créer le fichier .gitignore pour les projets FastAPI"
git commit -m "docs: ajouter le plan de démarrage et les messages de commit"

# Pour le démarrage réussi du serveur
git commit -m "feat(infra): démarrer le serveur FastAPI avec succès"
git commit -m "fix(env): corriger les variables d'environnement manquantes"
```

## Bonnes Pratiques

1. **Messages descriptifs** : Expliquez le "pourquoi" pas juste le "quoi"
2. **Anglais recommandé** : Pour la collaboration internationale
3. **Longueur limitée** : Maximum 72 caractères pour le sujet
4. **Corps optionnel** : Pour les explications détaillées

## Exemple Complet
```bash
git commit -m "feat(auth): implémenter l'authentification JWT

- Ajouter la création de tokens d'accès et de rafraîchissement
- Implémenter la vérification des tokens via middleware
- Ajouter la gestion des permissions utilisateur
- Sécuriser les endpoints avec Bearer token"
```

## Workflow Recommandé
1. `git add .` pour ajouter tous les changements
2. `git status` pour vérifier les fichiers à commiter
3. `git commit -m "type(scope): description"` avec le message approprié
4. `git push origin main` pour pousser les changements