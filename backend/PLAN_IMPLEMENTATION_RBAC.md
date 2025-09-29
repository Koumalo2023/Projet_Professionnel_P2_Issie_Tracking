# Plan d'Implémentation RBAC - Rôles et Autorisations

## 📅 Date du plan
24 septembre 2025

## 🎯 Objectif
Mettre en place un système RBAC (Role-Based Access Control) professionnel conforme aux spécifications du document [`GESTION_ROLES_AUTORISATIONS.md`](backend/GESTION_ROLES_AUTORISATIONS.md:1)

## 🏗️ Architecture Globale

### **Structure des composants à créer :**
```
backend/app/
├── models/
│   ├── role.py                    # Modèles RBAC
│   └── (mise à jour des modèles existants)
├── auth/
│   ├── permission_system.py       # Système centralisé de permissions
│   ├── permission_decorators.py   # Décorateurs pour les endpoints
│   └── (mise à jour de permissions.py)
├── middleware/
│   └── authorization.py           # Middleware d'autorisation
└── scripts/
    └── migrate_rbac.py            # Scripts de migration
```

## 📋 Plan d'Exécution Détaillé

### **Phase 1 : Modèles de Données (2-3 jours)**

#### **1.1 Création des modèles RBAC** ([`role.py`](backend/app/models/role.py:1))
```python
# Modèles à implémenter :
- Role (rôles système et projet)
- Permission (permissions granulaires)
- UserRole (rôles système des utilisateurs)
- ProjectRole (rôles spécifiques aux projets)
- RolePermission (association rôles-permissions)
```

#### **1.2 Mise à jour des modèles existants**
- **User** : Ajout relation vers UserRole
- **Project** : Ajout relation vers ProjectRole, remplacement author_id par owner_id
- **Contributor** : Rétrocompatibilité pendant la transition

### **Phase 2 : Système de Permissions (3-4 jours)**

#### **2.1 Implémentation du PermissionSystem** ([`permission_system.py`](backend/app/auth/permission_system.py:1))
- Classe centrale de gestion des permissions
- Méthodes : `has_permission()`, `get_user_permissions()`, `get_user_roles()`
- Cache des permissions pour performance

#### **2.2 Décorateurs de permission** ([`permission_decorators.py`](backend/app/auth/permission_decorators.py:1))
- `@require_permission(resource, action)`
- `@require_role(role_name)`
- Intégration avec l'authentification existante

#### **2.3 Middleware d'autorisation** ([`authorization.py`](backend/app/middleware/authorization.py:1))
- Vérification globale des permissions
- Logging des accès refusés
- Gestion des erreurs d'autorisation

### **Phase 3 : Migration des Données (2-3 jours)**

#### **3.1 Scripts de migration** ([`migrate_rbac.py`](backend/scripts/migrate_rbac.py:1))
- Migration des contributeurs vers ProjectRole
- Attribution des rôles système par défaut
- Vérification de l'intégrité des données

#### **3.2 Données initiales**
- Rôles système prédéfinis (Super Admin, Admin, Manager, User)
- Rôles projet prédéfinis (Owner, Admin, Developer, Reviewer, Viewer)
- Matrice de permissions complète

### **Phase 4 : Intégration Contrôleurs (3-4 jours)**

#### **4.1 Mise à jour progressive des contrôleurs**
- **ProjectController** : Gestion fine des permissions
- **IssueController** : Permissions par issue
- **CommentController** : Permissions par commentaire
- **ContributorController** : Évolution vers la gestion des rôles

#### **4.2 Rétrocompatibilité**
- Wrappers pour l'ancien système de permissions
- Migration progressive sans rupture
- Tests de régression complets

### **Phase 5 : Tests et Validation (2 jours)**

#### **5.1 Tests unitaires**
- PermissionSystem
- Décorateurs de permission
- Middleware d'autorisation

#### **5.2 Tests d'intégration**
- Scénarios complets d'utilisation
- Tests de performance
- Tests de sécurité

#### **5.3 Tests de migration**
- Validation des données migrées
- Tests de rollback
- Performance post-migration

## 🔧 Spécifications Techniques Détaillées

### **1. Matrice des Permissions**

#### **Rôles Système (4 rôles) :**
- **Super Admin** : Accès complet (toutes les permissions)
- **Admin** : Gestion utilisateurs + projets + configuration
- **Manager** : Création/gestion projets + équipes
- **User** : Accès basique (rôle par défaut)

#### **Rôles Projet (5 rôles) :**
- **Project Owner** : Toutes les actions sur le projet
- **Project Admin** : Gestion membres + configuration
- **Developer** : Création/modification issues + commentaires
- **Reviewer** : Lecture/commentaires + validation
- **Viewer** : Lecture seule

### **2. Resources et Actions**

#### **Resources :**
- `user` : Gestion des utilisateurs
- `project` : Gestion des projets
- `issue` : Gestion des issues
- `comment` : Gestion des commentaires
- `contributor` : Gestion des contributeurs
- `system` : Configuration système

#### **Actions :**
- `create` : Création de ressource
- `read` : Lecture de ressource
- `update` : Modification de ressource
- `delete` : Suppression de ressource
- `manage` : Gestion complète

### **3. API des Permissions**

```python
# Exemple d'usage
from app.auth.permission_decorators import require_permission

@router.post("/projects")
@require_permission("project", "create")
def create_project(...):
    # Logique métier
    pass

@router.put("/projects/{project_id}")
@require_permission("project", "update", project_param="project_id")
def update_project(project_id: int, ...):
    # Vérification spécifique au projet
    pass
```

## 🚀 Ordre d'Implémentation Recommandé

### **Séquence logique :**
1. **Modèles RBAC** (base de données)
2. **PermissionSystem** (cœur logique)
3. **Décorateurs** (interface développeurs)
4. **Migration données** (transition)
5. **Mise à jour contrôleurs** (intégration)
6. **Tests complets** (validation)

### **Priorités :**
- **Haute** : Rôles projet (impact immédiat sur l'usage)
- **Moyenne** : Rôles système (administration)
- **Basse** : Optimisations avancées (cache, performance)

## ⚠️ Risques Identifiés et Mitigations

### **Risque 1 : Rupture de compatibilité**
- **Mitigation** : Wrappers de rétrocompatibilité, migration progressive
- **Plan B** : Rollback scripté, sauvegardes régulières

### **Risque 2 : Performance**
- **Mitigation** : Cache des permissions, requêtes optimisées
- **Surveillance** : Métriques de performance post-déploiement

### **Risque 3 : Complexité**
- **Mitigation** : Documentation détaillée, exemples concrets
- **Formation** : Guide de migration pour les développeurs

## 📊 Métriques de Succès

### **Techniques :**
- ✅ 100% des endpoints protégés par RBAC
- ✅ Temps de réponse < 50ms pour les vérifications de permission
- ✅ 0 erreur de migration des données
- ✅ 100% de couverture de tests

### **Fonctionnelles :**
- ✅ Administration centralisée des permissions
- ✅ Expérience utilisateur améliorée
- ✅ Maintenance simplifiée

## 🗓️ Planning Estimé

### **Durée totale : 10-14 jours**
- **Phase 1** : 2-3 jours (modèles)
- **Phase 2** : 3-4 jours (système)
- **Phase 3** : 2-3 jours (migration)
- **Phase 4** : 3-4 jours (intégration)
- **Phase 5** : 2 jours (tests)

### **Livrables par phase :**
- **J+3** : Modèles RBAC opérationnels
- **J+7** : Système de permissions fonctionnel
- **J+10** : Migration données complète
- **J+14** : Système RBAC en production

## ✅ Critères d'Acceptation

### **Fonctionnels :**
- [ ] Toutes les permissions du document implémentées
- [ ] Interface cohérente avec l'existant
- [ ] Rétrocompatibilité maintenue
- [ ] Performance acceptable

### **Techniques :**
- [ ] Code propre et documenté
- [ ] Tests automatisés complets
- [ ] Logs d'audit fonctionnels
- [ ] Documentation utilisateur

## 🔮 Prochaines Étapes Immédiates

1. **Créer les modèles RBAC** selon les spécifications
2. **Implémenter le PermissionSystem** centralisé
3. **Développer les décorateurs** de permission
4. **Préparer les scripts** de migration

**Statut du plan :** ✅ **APPROUVÉ** - Prêt pour l'exécution