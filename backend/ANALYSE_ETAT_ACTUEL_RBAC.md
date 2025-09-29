# Analyse de l'État Actuel - Gestion des Rôles et Autorisations

## 📅 Date de l'analyse
24 septembre 2025

## 🔍 État Actuel des Modèles de Données

### 1. **Modèle Utilisateur ([`user.py`](backend/app/models/user.py:8))**
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer)
    can_be_contacted = Column(Boolean, default=False)
    can_data_be_shared = Column(Boolean, default=False)
    
    # Relations existantes
    projects = relationship("Project", back_populates="author")
    issues = relationship("Issue", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    contributions = relationship("Contributor", back_populates="user")
```

### 2. **Modèle Projet ([`project.py`](backend/app/models/project.py:5))**
```python
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    type = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    # Relations existantes
    author = relationship("User", back_populates="projects")
    issues = relationship("Issue", back_populates="project")
    contributors = relationship("Contributor", back_populates="project")
```

### 3. **Modèle Contributeur ([`contributor.py`](backend/app/models/contributor.py:5))**
```python
class Contributor(Base):
    __tablename__ = "contributors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Relations existantes
    user = relationship("User", back_populates="contributions")
    project = relationship("Project", back_populates="contributors")
```

### 4. **Système de Permissions Actuel ([`permissions.py`](backend/app/auth/permissions.py:9))**
```python
def is_project_contributor(project_id: int, user: User, db: Session) -> User:
    """
    Vérifie si l'utilisateur est un contributeur du projet.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.id not in [contributor.user_id for contributor in project.contributors]:
        raise HTTPException(status_code=403, detail="You are not a contributor to this project")
    return user
```

## ⚠️ Limitations Identifiées (Confirmées)

### 1. **Absence de Hiérarchie de Rôles** ✅ **CONFIRMÉ**
- Système binaire : Contributeur vs Non-contributeur
- Aucune distinction entre propriétaire, administrateur, développeur, viewer
- Impossible de définir des permissions granulaires

### 2. **Permissions par Projet Uniquement** ✅ **CONFIRMÉ**
- Pas de permissions globales (admin système)
- Pas de permissions par module (projets, issues, commentaires)
- Vérifications limitées à l'accès au projet

### 3. **Vérifications Manuelles et Redondantes** ✅ **CONFIRMÉ**
- Chaque endpoint doit appeler manuellement `is_project_contributor`
- Logique de permission dispersée dans les contrôleurs
- Risque élevé d'incohérences

## 📊 Analyse de l'Impact sur l'Architecture Actuelle

### **Points Forts de l'État Actuel**
- ✅ Structure de base solide (User, Project, Contributor)
- ✅ Relations SQLAlchemy bien définies
- ✅ Authentification JWT déjà en place
- ✅ Gestion des exceptions professionnelle récemment implémentée

### **Points à Améliorer**
- 🔄 Système de permissions trop basique
- 🔄 Absence de rôles et hiérarchie
- 🔄 Vérifications d'accès manuelles
- 🔄 Pas de gestion centralisée des autorisations

## 🎯 Architecture RBAC Proposée - Adaptation au Contexte

### **Modèle de Données à Implémenter**

#### **Nouveaux Modèles Nécessaires :**
1. **`Role`** - Rôles système et projet
2. **`Permission`** - Permissions granulaires
3. **`UserRole`** - Rôles système des utilisateurs
4. **`ProjectRole`** - Rôles spécifiques aux projets
5. **`RolePermission`** - Association rôles-permissions

#### **Migration du Modèle Existante :**
- **`Contributor`** → Devient une spécialisation de `ProjectRole`
- **Relations existantes** : À préserver et enrichir

### **Matrice des Permissions - Adaptation**

#### **Rôles Système (Nouveaux) :**
- **Super Admin** : Accès complet système
- **Admin** : Gestion utilisateurs et projets
- **Manager** : Création/gestion projets
- **User** : Utilisateur standard (rôle par défaut)

#### **Rôles Projet (Évolution de Contributor) :**
- **Project Owner** : Créateur du projet (remplace `author_id`)
- **Project Admin** : Administration du projet
- **Developer** : Développeur actif
- **Reviewer** : Relecteur technique
- **Viewer** : Observateur (remplace contributeur basique)

## 🔄 Plan de Migration - Spécifique au Contexte

### **Phase 1 : Préparation (1 semaine)**
- [ ] Créer les modèles RBAC sans affecter les modèles existants
- [ ] Définir la matrice de permissions adaptée au contexte actuel
- [ ] Créer les scripts de migration progressive
- [ ] Implémenter le système de permission centralisé

### **Phase 2 : Transition (2 semaines)**
- [ ] Mettre à jour les contrôleurs avec le nouveau système
- [ ] Implémenter les décorateurs de permission rétrocompatibles
- [ ] Migrer progressivement les contributeurs vers les rôles
- [ ] Maintenir la compatibilité avec l'ancien système

### **Phase 3 : Consolidation (1 semaine)**
- [ ] Supprimer l'ancien système de permissions
- [ ] Finaliser la migration des données
- [ ] Tests complets de régression
- [ ] Documentation mise à jour

## 🛡️ Considérations de Migration

### **1. Rétrocompatibilité**
- Maintenir l'API existante pendant la transition
- Fournir des wrappers pour l'ancien système
- Migration progressive sans interruption de service

### **2. Gestion des Données**
- Scripts de migration incrémentale
- Sauvegarde des données existantes
- Rollback planifié en cas de problème

### **3. Impact sur le Code Existant**
- Minimiser les modifications des contrôleurs existants
- Utiliser l'injection de dépendances existante
- Lever des exceptions compatibles avec le nouveau système

## 📈 Métriques de Succès Spécifiques

### **Pour cette Migration :**
- **Temps d'indisponibilité** : 0 heure (migration progressive)
- **Compatibilité API** : 100% maintenue
- **Performance** : Impact < 2% sur le temps de réponse
- **Couverture tests** : 100% des cas d'usage testés

## ✅ Prochaines Étapes Immédiates

1. **Examiner les contrôleurs existants** pour comprendre l'usage actuel des permissions
2. **Créer les modèles RBAC** en respectant l'architecture existante
3. **Définir la stratégie de migration** progressive et sécurisée

**État de l'analyse :** ✅ **COMPLÈTE** - Prêt pour la planification détaillée