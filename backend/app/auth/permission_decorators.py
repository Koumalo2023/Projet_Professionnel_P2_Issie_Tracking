# app/auth/permission_decorators.py
"""
Décorateurs de permission pour sécuriser les endpoints FastAPI
Permet de vérifier les autorisations des utilisateurs de manière déclarative
"""

from functools import wraps
from typing import List, Optional, Callable, Any
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.auth_utils import get_current_user
from app.auth.permission_system import (
    require_permission, 
    require_any_permission, 
    require_all_permissions,
    check_resource_access
)
from app.models.user import User


def permission_required(permission_name: str, project_id_param: Optional[str] = None):
    """
    Décorateur pour vérifier qu'un utilisateur a une permission spécifique
    
    Args:
        permission_name: Nom de la permission requise
        project_id_param: Nom du paramètre de route contenant l'ID du projet (optionnel)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            request: Request,
            *args,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            **kwargs
        ) -> Any:
            
            # Extraire l'ID du projet si spécifié
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if project_id is None:
                    # Essayer de récupérer depuis les paramètres de query
                    project_id = request.query_params.get(project_id_param)
            
            # Vérifier la permission
            await require_permission(permission_name, current_user, db, project_id)
            
            # Exécuter la fonction originale
            return await func(request, *args, db=db, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def any_permission_required(permission_names: List[str], project_id_param: Optional[str] = None):
    """
    Décorateur pour vérifier qu'un utilisateur a au moins une des permissions spécifiées
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            request: Request,
            *args,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            **kwargs
        ) -> Any:
            
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if project_id is None:
                    project_id = request.query_params.get(project_id_param)
            
            await require_any_permission(permission_names, current_user, db, project_id)
            return await func(request, *args, db=db, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def all_permissions_required(permission_names: List[str], project_id_param: Optional[str] = None):
    """
    Décorateur pour vérifier qu'un utilisateur a toutes les permissions spécifiées
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            request: Request,
            *args,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            **kwargs
        ) -> Any:
            
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if project_id is None:
                    project_id = request.query_params.get(project_id_param)
            
            await require_all_permissions(permission_names, current_user, db, project_id)
            return await func(request, *args, db=db, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def resource_access_required(resource: str, action: str, project_id_param: Optional[str] = None):
    """
    Décorateur pour vérifier l'accès à une ressource avec une action spécifique
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            request: Request,
            *args,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            **kwargs
        ) -> Any:
            
            project_id = None
            if project_id_param:
                project_id = kwargs.get(project_id_param)
                if project_id is None:
                    project_id = request.query_params.get(project_id_param)
            
            await check_resource_access(resource, action, current_user, db, project_id)
            return await func(request, *args, db=db, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


# Décorateurs prédéfinis pour les cas d'usage courants
def admin_required(func: Callable) -> Callable:
    """Décorateur pour restreindre l'accès aux administrateurs"""
    return permission_required("system_config")(func)


def project_owner_required(project_id_param: str = "project_id"):
    """Décorateur pour restreindre l'accès aux propriétaires de projet"""
    return permission_required("project_manage", project_id_param)


def project_admin_required(project_id_param: str = "project_id"):
    """Décorateur pour restreindre l'accès aux administrateurs de projet"""
    return any_permission_required(["project_manage", "project_admin"], project_id_param)


def project_member_required(project_id_param: str = "project_id"):
    """Décorateur pour restreindre l'accès aux membres du projet"""
    return any_permission_required([
        "project_read", "issue_read", "comment_read"
    ], project_id_param)


def can_manage_project(project_id_param: str = "project_id"):
    """Décorateur pour la gestion complète d'un projet"""
    return all_permissions_required([
        "project_read", "project_update", "project_manage"
    ], project_id_param)


def can_manage_issues(project_id_param: str = "project_id"):
    """Décorateur pour la gestion des issues"""
    return all_permissions_required([
        "issue_create", "issue_read", "issue_update", "issue_delete"
    ], project_id_param)


def can_manage_comments(project_id_param: str = "project_id"):
    """Décorateur pour la gestion des commentaires"""
    return all_permissions_required([
        "comment_create", "comment_read", "comment_update", "comment_delete"
    ], project_id_param)


def can_manage_members(project_id_param: str = "project_id"):
    """Décorateur pour la gestion des membres"""
    return all_permissions_required([
        "project_member_add", "project_member_remove", "project_member_manage"
    ], project_id_param)


# Décorateurs pour les actions spécifiques
def can_create_project(func: Callable) -> Callable:
    """Décorateur pour créer un projet"""
    return permission_required("project_create")(func)


def can_read_project(project_id_param: str = "project_id"):
    """Décorateur pour lire un projet"""
    return permission_required("project_read", project_id_param)


def can_update_project(project_id_param: str = "project_id"):
    """Décorateur pour modifier un projet"""
    return permission_required("project_update", project_id_param)


def can_delete_project(project_id_param: str = "project_id"):
    """Décorateur pour supprimer un projet"""
    return permission_required("project_delete", project_id_param)


def can_create_issue(project_id_param: str = "project_id"):
    """Décorateur pour créer une issue"""
    return permission_required("issue_create", project_id_param)


def can_read_issue(project_id_param: str = "project_id"):
    """Décorateur pour lire une issue"""
    return permission_required("issue_read", project_id_param)


def can_update_issue(project_id_param: str = "project_id"):
    """Décorateur pour modifier une issue"""
    return permission_required("issue_update", project_id_param)


def can_delete_issue(project_id_param: str = "project_id"):
    """Décorateur pour supprimer une issue"""
    return permission_required("issue_delete", project_id_param)


def can_create_comment(project_id_param: str = "project_id"):
    """Décorateur pour créer un commentaire"""
    return permission_required("comment_create", project_id_param)


def can_read_comment(project_id_param: str = "project_id"):
    """Décorateur pour lire un commentaire"""
    return permission_required("comment_read", project_id_param)


def can_update_comment(project_id_param: str = "project_id"):
    """Décorateur pour modifier un commentaire"""
    return permission_required("comment_update", project_id_param)


def can_delete_comment(project_id_param: str = "project_id"):
    """Décorateur pour supprimer un commentaire"""
    return permission_required("comment_delete", project_id_param)