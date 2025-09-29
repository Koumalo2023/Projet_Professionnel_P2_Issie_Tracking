# app/auth/permission_system.py
"""
Système centralisé de gestion des permissions RBAC
Vérifie les autorisations des utilisateurs basées sur leurs rôles
"""

from typing import List, Dict, Optional, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.role import Role, Permission, UserRole, ProjectRole
from app.auth.permission_matrix import (
    PERMISSIONS, 
    ROLE_SYSTEM_PERMISSIONS, 
    ROLE_PROJECT_PERMISSIONS,
    get_permission_name,
    get_role_permissions
)
from app.exceptions.http_exceptions import ForbiddenException


class PermissionSystem:
    """Système centralisé de gestion des permissions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def has_permission(self, user: User, permission_name: str, project_id: Optional[int] = None) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique
        
        Args:
            user: L'utilisateur à vérifier
            permission_name: Nom de la permission (ex: "project_read")
            project_id: ID du projet pour les permissions spécifiques au projet
        
        Returns:
            bool: True si l'utilisateur a la permission
        """
        # Récupérer tous les rôles de l'utilisateur
        user_roles = self._get_user_roles(user.id)
        project_roles = self._get_user_project_roles(user.id, project_id) if project_id else []
        
        # Vérifier les permissions système
        for role_name in user_roles:
            if permission_name in ROLE_SYSTEM_PERMISSIONS.get(role_name, []):
                return True
        
        # Vérifier les permissions projet
        for role_name in project_roles:
            if permission_name in ROLE_PROJECT_PERMISSIONS.get(role_name, []):
                return True
        
        return False
    
    def has_any_permission(self, user: User, permission_names: List[str], project_id: Optional[int] = None) -> bool:
        """
        Vérifie si un utilisateur a au moins une des permissions spécifiées
        """
        for permission_name in permission_names:
            if self.has_permission(user, permission_name, project_id):
                return True
        return False
    
    def has_all_permissions(self, user: User, permission_names: List[str], project_id: Optional[int] = None) -> bool:
        """
        Vérifie si un utilisateur a toutes les permissions spécifiées
        """
        for permission_name in permission_names:
            if not self.has_permission(user, permission_name, project_id):
                return False
        return True
    
    def get_user_permissions(self, user: User, project_id: Optional[int] = None) -> Set[str]:
        """
        Retourne toutes les permissions d'un utilisateur
        """
        permissions = set()
        
        # Permissions système
        user_roles = self._get_user_roles(user.id)
        for role_name in user_roles:
            permissions.update(ROLE_SYSTEM_PERMISSIONS.get(role_name, []))
        
        # Permissions projet
        if project_id:
            project_roles = self._get_user_project_roles(user.id, project_id)
            for role_name in project_roles:
                permissions.update(ROLE_PROJECT_PERMISSIONS.get(role_name, []))
        
        return permissions
    
    def _get_user_roles(self, user_id: int) -> List[str]:
        """Récupère les noms des rôles système d'un utilisateur"""
        user_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
        return [user_role.role.name for user_role in user_roles if user_role.role]
    
    def _get_user_project_roles(self, user_id: int, project_id: int) -> List[str]:
        """Récupère les noms des rôles projet d'un utilisateur pour un projet spécifique"""
        project_roles = self.db.query(ProjectRole).filter(
            ProjectRole.user_id == user_id,
            ProjectRole.project_id == project_id
        ).all()
        return [project_role.role.name for project_role in project_roles if project_role.role]
    
    def can_access_resource(self, user: User, resource: str, action: str, project_id: Optional[int] = None) -> bool:
        """
        Vérifie l'accès à une ressource avec une action spécifique
        Utilise la matrice de permissions pour convertir ressource/action en nom de permission
        """
        try:
            permission_name = get_permission_name(resource, action)
            return self.has_permission(user, permission_name, project_id)
        except ValueError:
            # Permission non définie dans la matrice
            return False


# Dépendances FastAPI pour l'injection
def get_permission_system(db: Session = Depends(get_db)) -> PermissionSystem:
    """Dépendance pour obtenir le système de permissions"""
    return PermissionSystem(db)


# Fonctions utilitaires pour les décorateurs
async def require_permission(
    permission_name: str,
    user: User,
    db: Session,
    project_id: Optional[int] = None
):
    """
    Vérifie qu'un utilisateur a une permission spécifique
    Lève une exception ForbiddenException si la permission est refusée
    """
    permission_system = PermissionSystem(db)
    if not permission_system.has_permission(user, permission_name, project_id):
        raise ForbiddenException(
            detail=f"Permission refusée: {permission_name}",
            error_code="PERMISSION_DENIED"
        )


async def require_any_permission(
    permission_names: List[str],
    user: User,
    db: Session,
    project_id: Optional[int] = None
):
    """
    Vérifie qu'un utilisateur a au moins une des permissions spécifiées
    """
    permission_system = PermissionSystem(db)
    if not permission_system.has_any_permission(user, permission_names, project_id):
        raise ForbiddenException(
            detail=f"Aucune permission parmi: {', '.join(permission_names)}",
            error_code="PERMISSION_DENIED"
        )


async def require_all_permissions(
    permission_names: List[str],
    user: User,
    db: Session,
    project_id: Optional[int] = None
):
    """
    Vérifie qu'un utilisateur a toutes les permissions spécifiées
    """
    permission_system = PermissionSystem(db)
    if not permission_system.has_all_permissions(user, permission_names, project_id):
        raise ForbiddenException(
            detail=f"Permissions manquantes parmi: {', '.join(permission_names)}",
            error_code="PERMISSION_DENIED"
        )


# Fonction pour vérifier l'accès aux ressources
async def check_resource_access(
    resource: str,
    action: str,
    user: User,
    db: Session,
    project_id: Optional[int] = None
):
    """
    Vérifie l'accès à une ressource avec une action spécifique
    """
    permission_system = PermissionSystem(db)
    if not permission_system.can_access_resource(user, resource, action, project_id):
        raise ForbiddenException(
            detail=f"Accès refusé à {resource} pour l'action {action}",
            error_code="RESOURCE_ACCESS_DENIED"
        )
