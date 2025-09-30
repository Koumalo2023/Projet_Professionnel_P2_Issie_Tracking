# backend/app/exceptions/session_exceptions.py
"""
Exceptions spécifiques à la gestion des sessions
"""

from app.exceptions.http_exceptions import HTTPException


class SessionNotFoundException(HTTPException):
    """Exception levée quand une session n'est pas trouvée"""
    
    def __init__(self, message: str = "Session non trouvée"):
        super().__init__(
            status_code=404,
            detail=message,
            error_code="SESSION_NOT_FOUND"
        )


class SessionExpiredException(HTTPException):
    """Exception levée quand une session est expirée"""
    
    def __init__(self, message: str = "Session expirée"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="SESSION_EXPIRED"
        )


class InvalidSessionException(HTTPException):
    """Exception levée quand une session est invalide"""
    
    def __init__(self, message: str = "Session invalide"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="INVALID_SESSION"
        )


class TooManyActiveSessionsException(HTTPException):
    """Exception levée quand un utilisateur a trop de sessions actives"""
    
    def __init__(self, max_sessions: int, message: str = None):
        if not message:
            message = f"Trop de sessions actives. Maximum autorisé: {max_sessions}"
        
        super().__init__(
            status_code=403,
            detail=message,
            error_code="TOO_MANY_SESSIONS"
        )


class SessionSecurityException(HTTPException):
    """Exception levée pour des problèmes de sécurité liés aux sessions"""
    
    def __init__(self, message: str = "Problème de sécurité avec la session"):
        super().__init__(
            status_code=403,
            detail=message,
            error_code="SESSION_SECURITY_ERROR"
        )


class CSRFValidationException(HTTPException):
    """Exception levée quand la validation CSRF échoue"""
    
    def __init__(self, message: str = "Token CSRF invalide"):
        super().__init__(
            status_code=403,
            detail=message,
            error_code="CSRF_VALIDATION_FAILED"
        )


class RefreshTokenException(HTTPException):
    """Exception levée quand le rafraîchissement du token échoue"""
    
    def __init__(self, message: str = "Échec du rafraîchissement du token"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="REFRESH_TOKEN_FAILED"
        )