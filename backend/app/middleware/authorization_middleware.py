# app/middleware/authorization_middleware.py
"""
Middleware d'autorisation pour vérifier les permissions des utilisateurs
S'intègre avec le système RBAC pour contrôler l'accès aux endpoints
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.auth_utils import get_current_user_from_request
from app.auth.permission_system import PermissionSystem
from app.models.user import User
from app.exceptions.http_exceptions import ForbiddenException
from app.utils.logger import log_error


class AuthorizationMiddleware:
    """Middleware d'autorisation RBAC"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """
        Intercepte les requêtes et vérifie les autorisations
        """
        # Ignorer les endpoints publics
        if self._is_public_endpoint(request):
            return await call_next(request)
        
        # Vérifier l'authentification
        try:
            # Obtenir la base de données et l'utilisateur courant
            db = next(get_db())
            current_user = await get_current_user_from_request(request, db)
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentification requise"
                )
            
            # Vérifier les permissions pour cette route
            if not self._has_permission(request, current_user, db):
                raise ForbiddenException(
                    detail="Accès refusé - Permissions insuffisantes",
                    error_code="AUTHORIZATION_DENIED"
                )
            
            # Ajouter l'utilisateur au contexte de la requête
            request.state.current_user = current_user
            request.state.db = db
            
            # Continuer avec la requête
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            log_error(f"Erreur d'autorisation: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "error_code": getattr(e, 'error_code', 'AUTH_ERROR')}
            )
        except Exception as e:
            log_error(f"Erreur inattendue dans le middleware d'autorisation: {str(e)}", exc_info=e)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Erreur interne du serveur", "error_code": "INTERNAL_ERROR"}
            )
        finally:
            # Fermer la session de base de données
            if 'db' in locals():
                db.close()
    
    def _is_public_endpoint(self, request: Request) -> bool:
        """
        Détermine si un endpoint est public (ne nécessite pas d'autorisation)
        """
        public_paths = [
            "/auth/login",
            "/auth/refresh",
            "/users/signup",
            "/users/login",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        # Vérifier si le chemin correspond à un endpoint public
        path = request.url.path
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _has_permission(self, request: Request, user: User, db: Session) -> bool:
        """
        Vérifie si l'utilisateur a les permissions nécessaires pour cette route
        """
        permission_system = PermissionSystem(db)
        
        # Extraire l'ID du projet des paramètres de route si présent
        project_id = self._extract_project_id(request)
        
        # Mapper les méthodes HTTP aux actions
        action = self._map_method_to_action(request.method)
        
        # Mapper les chemins aux ressources
        resource = self._map_path_to_resource(request.url.path)
        
        # Vérifier l'accès à la ressource
        return permission_system.can_access_resource(user, resource, action, project_id)
    
    def _extract_project_id(self, request: Request) -> int | None:
        """
        Extrait l'ID du projet des paramètres de route
        """
        try:
            # Vérifier les paramètres de route pour project_id
            if "project_id" in request.path_params:
                return int(request.path_params["project_id"])
            
            # Vérifier les paramètres de query
            project_id = request.query_params.get("project_id")
            if project_id:
                return int(project_id)
                
            return None
        except (ValueError, TypeError):
            return None
    
    def _map_method_to_action(self, method: str) -> str:
        """
        Mappe les méthodes HTTP aux actions de permission
        """
        method_action_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        return method_action_map.get(method, "read")
    
    def _map_path_to_resource(self, path: str) -> str:
        """
        Mappe les chemins d'URL aux ressources de permission
        """
        # Supprimer le préfixe /api/v1 si présent
        if path.startswith("/api/v1"):
            path = path[7:]
        
        # Mapper les chemins aux ressources
        path_resource_map = {
            "/users": "user",
            "/projects": "project",
            "/issues": "issue",
            "/comments": "comment",
            "/contributors": "contributor",
            "/auth": "system"
        }
        
        # Trouver la ressource correspondante
        for prefix, resource in path_resource_map.items():
            if path.startswith(prefix):
                return resource
        
        # Ressource par défaut
        return "system"


# Fonction pour créer le middleware
def create_authorization_middleware(app):
    """Factory pour créer le middleware d'autorisation"""
    return AuthorizationMiddleware(app)


# Décorateur pour désactiver l'autorisation sur des endpoints spécifiques
def public_endpoint(func):
    """
    Décorateur pour marquer un endpoint comme public (ne nécessite pas d'autorisation)
    """
    func.is_public = True
    return func


# Middleware simplifié pour l'ajout à l'application FastAPI
async def authorization_middleware(request: Request, call_next):
    """
    Version simplifiée du middleware pour l'utilisation avec FastAPI
    """
    middleware = AuthorizationMiddleware(call_next)
    return await middleware(request, call_next)