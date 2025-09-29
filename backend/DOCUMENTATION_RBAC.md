# Documentation de l'Architecture RBAC

## Vue d'ensemble

Le système RBAC (Role-Based Access Control) a été implémenté pour remplacer le système de permissions binaire existant. Cette architecture permet une gestion fine des autorisations basée sur les rôles des utilisateurs.

## Architecture Technique

### 1. Modèles de Données

#### [`Role`](backend/app/models/role.py:1)
```python
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_system_role = Column(Boolean, default=False)
```

#### [`Permission`](backend/app/models/role.py:1)
```python
class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(String(255))
```

#### [`UserRole`](backend/app/models/role.py:1) et [`ProjectRole`](backend/app/models/role.py:1)
- `UserRole`: Rôles système assignés aux utilisateurs
- `ProjectRole`: Rôles spécifiques aux projets

### 2. Matrice des Permissions

Le fichier [`permission_matrix.py`](backend/app/auth/permission_matrix.py:1) définit la structure complète des permissions :

```python
PERMISSIONS: List[Tuple[str, str, str, str]] = [
    ("user_create", "user", "create", "Créer un utilisateur"),
    ("project_read", "project", "read", "Lire un projet"),
    # ... autres permissions
]
```

#### Rôles Système
- **super_admin**: Accès complet au système
- **admin**: Gestion utilisateurs et projets
- **manager**: Création et gestion de projets
- **user**: Accès basique

#### Rôles Projet
- **project_owner**: Toutes les permissions sur un projet
- **project_admin**: Gestion complète d'un projet
- **developer**: Création et modification d'issues
- **reviewer**: Lecture et commentaires
- **viewer**: Lecture seule

### 3. Système de Permission Centralisé

Le [`PermissionSystem`](backend/app/auth/permission_system.py:1) gère la vérification des autorisations :

```python
class PermissionSystem:
    def has_permission(self, user: User, permission_name: str, project_id: Optional[int] = None) -> bool
    def has_any_permission(self, user: User, permission_names: List[str], project_id: Optional[int] = None) -> bool
    def has_all_permissions(self, user: User, permission_names: List[str], project_id: Optional[int] = None) -> bool
```

### 4. Décorateurs de Permission

Les [`décorateurs`](backend/app/auth/permission_decorators.py:1) permettent de sécuriser les endpoints :

```python
@permission_required("project_create")
@can_read_project("project_id")
@admin_required
```

### 5. Middleware d'Autorisation

Le [`middleware`](backend/app/middleware/authorization_middleware.py:1) vérifie automatiquement les permissions :

```python
class AuthorizationMiddleware:
    async def __call__(self, request: Request, call_next):
        # Vérification des permissions
```

## Flux d'Autorisation

### 1. Authentification
- L'utilisateur s'authentifie via JWT
- Le token contient les informations d'identité

### 2. Vérification des Permissions
1. **Middleware**: Vérifie l'accès basé sur la route et la méthode HTTP
2. **Décorateurs**: Vérification spécifique par endpoint
3. **Système Central**: Logique métier des permissions

### 3. Résultat
- ✅ Accès autorisé si les permissions sont suffisantes
- ❌ Accès refusé avec code HTTP 403

## Migration des Données

### Script de Migration
Le script [`init_rbac_data.py`](backend/scripts/init_rbac_data.py:1) initialise :
- Rôles système et projet
- Permissions disponibles
- Associations rôles-permissions
- Migration des contributeurs existants

### Migration Alembic
Le fichier [`001_init_rbac_tables.py`](backend/alembic/versions/001_init_rbac_tables.py:1) crée les tables nécessaires.

## Tests

Les tests [`test_rbac_system.py`](backend/tests/test_rbac_system.py:1) vérifient :
- ✅ Permissions des différents rôles
- ✅ Accès aux endpoints protégés
- ✅ Fonctionnement du middleware
- ✅ Intégration avec les contrôleurs

## Intégration avec l'Application

### Configuration dans [`main.py`](backend/app/main.py:1)
```python
from app.middleware.authorization_middleware import authorization_middleware

# Ajoute le middleware d'autorisation RBAC
app.middleware("http")(authorization_middleware)
```

### Mise à jour des Contrôleurs
Tous les contrôleurs ont été mis à jour avec les décorateurs appropriés :

- [`project_controller.py`](backend/app/controllers/project_controller.py:1)
- [`issue_controller.py`](backend/app/controllers/issue_controller.py:1)
- [`comment_controller.py`](backend/app/controllers/comment_controller.py:1)
- [`user_controller.py`](backend/app/controllers/user_controller.py:1)

## Avantages de la Nouvelle Architecture

### 1. Granularité
- Permissions fines par ressource et action
- Rôles spécifiques aux projets
- Séparation claire des responsabilités

### 2. Extensibilité
- Ajout facile de nouvelles permissions
- Création de rôles personnalisés
- Adaptation aux besoins métier

### 3. Sécurité
- Vérification centralisée des permissions
- Défense en profondeur (middleware + décorateurs)
- Journalisation des accès

### 4. Maintenance
- Code déclaratif avec les décorateurs
- Configuration centralisée dans la matrice
- Tests automatisés complets

## Bonnes Pratiques

### 1. Attribution des Rôles
- Utiliser le principe du moindre privilège
- Réviser régulièrement les attributions de rôles
- Documenter les responsabilités par rôle

### 2. Gestion des Permissions
- Ajouter de nouvelles permissions via la matrice
- Tester les permissions après modification
- Documenter les changements

### 3. Développement
- Utiliser les décorateurs appropriés
- Tester les autorisations dans les tests unitaires
- Vérifier les permissions côté serveur et client

## Déploiement

### 1. Migration
```bash
# Appliquer la migration Alembic
alembic upgrade head

# Initialiser les données RBAC
python scripts/init_rbac_data.py
```

### 2. Vérification
```bash
# Exécuter les tests
pytest tests/test_rbac_system.py -v
```

### 3. Monitoring
- Surveiller les logs d'autorisation
- Auditer régulièrement les accès
- Mettre à jour la documentation

## Conclusion

Le système RBAC implémenté offre une solution robuste et évolutive pour la gestion des autorisations. Il respecte les meilleures pratiques de sécurité tout en restant facile à maintenir et à étendre.

La documentation complète, les tests automatisés et les scripts de migration garantissent un déploiement sécurisé et fiable.