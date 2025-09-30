# backend/app/middleware/token_refresh_middleware.py
"""
Middleware pour le rafraîchissement automatique des tokens avec rotation sécurisée
Gère automatiquement le rafraîchissement des tokens expirés ou sur le point d'expirer
"""

import time
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.token_service import TokenService
from app.utils.logger import get_logger
from app.exceptions.session_exceptions import TokenExpiredException, InvalidTokenException

logger = get_logger(__name__)


class TokenRefreshMiddleware:
    """Middleware pour le rafraîchissement automatique des tokens"""
    
    def __init__(self, app):
        self.app = app
        self.refresh_threshold_seconds = 300  # 5 minutes avant expiration
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Intercepte les requêtes pour gérer le rafraîchissement automatique des tokens
        """
        # Ignore les requêtes qui ne nécessitent pas d'authentification
        if self._should_skip_middleware(request):
            return await call_next(request)
        
        # Vérifie la présence d'un token d'accès
        access_token = self._extract_access_token(request)
        if not access_token:
            return await call_next(request)
        
        # Vérifie la présence d'un token de rafraîchissement
        refresh_token = self._extract_refresh_token(request)
        if not refresh_token:
            return await call_next(request)
        
        try:
            # Crée une session de base de données
            db = next(get_db())
            token_service = TokenService(db)
            
            # Valide le token d'accès
            try:
                payload = token_service.validate_access_token(access_token)
                
                # Vérifie si le token est sur le point d'expirer
                if self._should_refresh_token(payload):
                    logger.info(f"Token sur le point d'expirer, tentative de rafraîchissement automatique")
                    
                    # Tente le rafraîchissement automatique
                    new_access_token, new_refresh_token, session = token_service.refresh_tokens(
                        old_refresh_token=refresh_token,
                        ip_address=request.client.host if request.client else "unknown",
                        user_agent=request.headers.get("user-agent")
                    )
                    
                    # Crée la réponse avec les nouveaux tokens
                    response = await call_next(request)
                    
                    # Ajoute les nouveaux tokens aux headers de réponse
                    response.headers["X-New-Access-Token"] = new_access_token
                    response.headers["X-New-Refresh-Token"] = new_refresh_token
                    response.headers["X-Token-Refreshed"] = "true"
                    
                    logger.info(f"Token rafraîchi automatiquement pour la session {session.id}")
                    
                    return response
                
            except TokenExpiredException:
                # Token expiré, tente le rafraîchissement
                logger.info("Token expiré, tentative de rafraîchissement automatique")
                
                try:
                    new_access_token, new_refresh_token, session = token_service.refresh_tokens(
                        old_refresh_token=refresh_token,
                        ip_address=request.client.host if request.client else "unknown",
                        user_agent=request.headers.get("user-agent")
                    )
                    
                    # Remplace le token d'accès dans la requête
                    request.headers.__dict__["_list"] = [
                        (b"authorization", f"Bearer {new_access_token}".encode()),
                        *[(k, v) for k, v in request.headers.items() if k.lower() != b"authorization"]
                    ]
                    
                    # Continue avec la nouvelle requête
                    response = await call_next(request)
                    
                    # Ajoute les nouveaux tokens aux headers
                    response.headers["X-New-Access-Token"] = new_access_token
                    response.headers["X-New-Refresh-Token"] = new_refresh_token
                    response.headers["X-Token-Refreshed"] = "true"
                    
                    logger.info(f"Token expiré rafraîchi automatiquement pour la session {session.id}")
                    
                    return response
                    
                except Exception as refresh_error:
                    logger.error(f"Échec du rafraîchissement automatique: {str(refresh_error)}")
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": "Token expiré et rafraîchissement automatique échoué",
                            "auto_refresh_failed": True
                        }
                    )
            
            # Token valide, pas besoin de rafraîchissement
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Erreur dans le middleware de rafraîchissement: {str(e)}")
            # En cas d'erreur, continue sans rafraîchissement
            return await call_next(request)
    
    def _should_skip_middleware(self, request: Request) -> bool:
        """
        Détermine si le middleware doit être ignoré pour cette requête
        """
        # Ignore les endpoints publics
        public_paths = {
            "/health",
            "/api/auth/login",
            "/api/auth/register", 
            "/api/auth/forgot-password",
            "/api/auth/reset-password",
            "/api/oauth",
            "/api/tokens/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        
        if request.url.path in public_paths:
            return True
        
        # Ignore les méthodes OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return True
        
        return False
    
    def _extract_access_token(self, request: Request) -> Optional[str]:
        """
        Extrait le token d'accès du header Authorization
        """
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Retire "Bearer "
        return None
    
    def _extract_refresh_token(self, request: Request) -> Optional[str]:
        """
        Extrait le token de rafraîchissement des headers ou cookies
        """
        # Cherche dans les headers personnalisés
        refresh_token = request.headers.get("x-refresh-token")
        if refresh_token:
            return refresh_token
        
        # Cherche dans les cookies
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            return refresh_token
        
        return None
    
    def _should_refresh_token(self, payload: Dict[str, Any]) -> bool:
        """
        Détermine si le token doit être rafraîchi automatiquement
        """
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            return False
        
        current_time = time.time()
        time_until_expiry = exp_timestamp - current_time
        
        # Rafraîchit si le token expire dans moins de 5 minutes
        return time_until_expiry <= self.refresh_threshold_seconds


# Fonction pour intégrer le middleware
def token_refresh_middleware(app):
    """Intègre le middleware de rafraîchissement automatique des tokens"""
    return TokenRefreshMiddleware(app)
