# app/auth/permission_matrix.py
"""
Matrice des permissions pour le système RBAC
Définit les permissions disponibles et leur association aux rôles
"""

from typing import Dict, List, Tuple

# =============================================================================
# PERMISSIONS DISPONIBLES
# =============================================================================

# Format: (nom, ressource, action, description)
PERMISSIONS: List[Tuple[str, str, str, str]] = [
    # Permissions globales (système)
    ("user_create", "user", "create", "Créer un utilisateur"),
    ("user_read", "user", "read", "Lire les informations utilisateur"),
    ("user_update", "user", "update", "Modifier un utilisateur"),
    ("user_delete", "user", "delete", "Supprimer un utilisateur"),
    ("user_manage", "user", "manage", "Gérer tous les utilisateurs"),
    
    ("project_create", "project", "create", "Créer un projet"),
    ("project_read_all", "project", "read_all", "Lire tous les projets"),
    ("project_manage_all", "project", "manage_all", "Gérer tous les projets"),
    
    ("system_config", "system", "config", "Configurer le système"),
    ("system_monitor", "system", "monitor", "Surveiller le système"),
    
    # Permissions par projet
    ("project_read", "project", "read", "Lire un projet"),
    ("project_update", "project", "update", "Modifier un projet"),
    ("project_delete", "project", "delete", "Supprimer un projet"),
    ("project_manage", "project", "manage", "Gérer un projet"),
    
    ("project_member_add", "project_member", "add", "Ajouter un membre au projet"),
    ("project_member_remove", "project_member", "remove", "Retirer un membre du projet"),
    ("project_member_manage", "project_member", "manage", "Gérer les membres du projet"),
    
    ("issue_create", "issue", "create", "Créer une issue"),
    ("issue_read", "issue", "read", "Lire une issue"),
    ("issue_update", "issue", "update", "Modifier une issue"),
    ("issue_delete", "issue", "delete", "Supprimer une issue"),
    ("issue_manage", "issue", "manage", "Gérer les issues"),
    
    ("comment_create", "comment", "create", "Créer un commentaire"),
    ("comment_read", "comment", "read", "Lire un commentaire"),
    ("comment_update", "comment", "update", "Modifier un commentaire"),
    ("comment_delete", "comment", "delete", "Supprimer un commentaire"),
    
    ("contributor_add", "contributor", "add", "Ajouter un contributeur"),
    ("contributor_remove", "contributor", "remove", "Retirer un contributeur"),
    ("contributor_manage", "contributor", "manage", "Gérer les contributeurs"),
]

# =============================================================================
# RÔLES SYSTÈME
# =============================================================================

ROLES_SYSTEM: List[Tuple[str, str, bool]] = [
    ("super_admin", "Super Administrateur - Accès complet au système", True),
    ("admin", "Administrateur - Gestion utilisateurs et projets", True),
    ("manager", "Manager - Création et gestion de projets", True),
    ("user", "Utilisateur standard - Accès basique", True),
]

# =============================================================================
# RÔLES PROJET
# =============================================================================

ROLES_PROJECT: List[Tuple[str, str]] = [
    ("project_owner", "Propriétaire du projet - Toutes les permissions"),
    ("project_admin", "Administrateur du projet - Gestion complète"),
    ("developer", "Développeur - Création et modification d'issues"),
    ("reviewer", "Relecteur - Lecture et commentaires"),
    ("viewer", "Observateur - Lecture seule"),
]

# =============================================================================
# ASSOCIATIONS RÔLES-PERMISSIONS
# =============================================================================

# Permissions par rôle système
ROLE_SYSTEM_PERMISSIONS: Dict[str, List[str]] = {
    "super_admin": [
        "user_create", "user_read", "user_update", "user_delete", "user_manage",
        "project_create", "project_read_all", "project_manage_all",
        "system_config", "system_monitor"
    ],
    "admin": [
        "user_create", "user_read", "user_update", "user_manage",
        "project_create", "project_read_all", "project_manage_all"
    ],
    "manager": [
        "project_create", "project_read_all"
    ],
    "user": [
        "project_create"
    ]
}

# Permissions par rôle projet
ROLE_PROJECT_PERMISSIONS: Dict[str, List[str]] = {
    "project_owner": [
        "project_read", "project_update", "project_delete", "project_manage",
        "project_member_add", "project_member_remove", "project_member_manage",
        "issue_create", "issue_read", "issue_update", "issue_delete", "issue_manage",
        "comment_create", "comment_read", "comment_update", "comment_delete",
        "contributor_add", "contributor_remove", "contributor_manage"
    ],
    "project_admin": [
        "project_read", "project_update", "project_manage",
        "project_member_add", "project_member_remove", "project_member_manage",
        "issue_create", "issue_read", "issue_update", "issue_delete", "issue_manage",
        "comment_create", "comment_read", "comment_update", "comment_delete",
        "contributor_add", "contributor_remove", "contributor_manage"
    ],
    "developer": [
        "project_read",
        "issue_create", "issue_read", "issue_update",
        "comment_create", "comment_read", "comment_update", "comment_delete"
    ],
    "reviewer": [
        "project_read",
        "issue_read",
        "comment_create", "comment_read", "comment_update"
    ],
    "viewer": [
        "project_read",
        "issue_read",
        "comment_read"
    ]
}

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_permission_name(resource: str, action: str) -> str:
    """Retourne le nom canonique d'une permission à partir de la ressource et de l'action"""
    for perm_name, perm_resource, perm_action, _ in PERMISSIONS:
        if perm_resource == resource and perm_action == action:
            return perm_name
    raise ValueError(f"Permission non trouvée pour {resource}:{action}")

def get_permission_description(permission_name: str) -> str:
    """Retourne la description d'une permission"""
    for perm_name, _, _, description in PERMISSIONS:
        if perm_name == permission_name:
            return description
    raise ValueError(f"Permission {permission_name} non trouvée")

def get_role_permissions(role_name: str, is_system_role: bool = True) -> List[str]:
    """Retourne les permissions d'un rôle"""
    if is_system_role:
        return ROLE_SYSTEM_PERMISSIONS.get(role_name, [])
    else:
        return ROLE_PROJECT_PERMISSIONS.get(role_name, [])

def get_all_permissions() -> List[Dict]:
    """Retourne toutes les permissions sous forme de dictionnaire"""
    return [
        {
            "name": name,
            "resource": resource,
            "action": action,
            "description": description
        }
        for name, resource, action, description in PERMISSIONS
    ]

def get_all_roles() -> Dict:
    """Retourne tous les rôles avec leurs permissions"""
    return {
        "system_roles": [
            {
                "name": name,
                "description": description,
                "is_system_role": is_system,
                "permissions": get_role_permissions(name, True)
            }
            for name, description, is_system in ROLES_SYSTEM
        ],
        "project_roles": [
            {
                "name": name,
                "description": description,
                "is_system_role": False,
                "permissions": get_role_permissions(name, False)
            }
            for name, description in ROLES_PROJECT
        ]
    }