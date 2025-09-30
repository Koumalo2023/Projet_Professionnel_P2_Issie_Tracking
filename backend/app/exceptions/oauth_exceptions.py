# app/exceptions/oauth_exceptions.py
"""
Exceptions spécifiques à l'authentification OAuth2
"""

from fastapi import status
from app.exceptions.http_exceptions import HTTPException


class OAuthException(HTTPException):
    """Exception de base pour les erreurs OAuth2"""
    
    def __init__(self, detail: str, error_code: str = "OAUTH_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class OAuthProviderNotConfiguredException(OAuthException):
    """Exception levée lorsque le provider OAuth2 n'est pas configuré"""
    
    def __init__(self, provider: str):
        super().__init__(
            detail=f"Le provider OAuth2 '{provider}' n'est pas configuré",
            error_code="OAUTH_PROVIDER_NOT_CONFIGURED"
        )


class OAuthStateNotFoundException(OAuthException):
    """Exception levée lorsque le state OAuth2 est introuvable"""
    
    def __init__(self):
        super().__init__(
            detail="Le token state OAuth2 est introuvable ou a expiré",
            error_code="OAUTH_STATE_NOT_FOUND"
        )


class OAuthStateExpiredException(OAuthException):
    """Exception levée lorsque le state OAuth2 a expiré"""
    
    def __init__(self):
        super().__init__(
            detail="Le token state OAuth2 a expiré. Veuillez recommencer le processus",
            error_code="OAUTH_STATE_EXPIRED"
        )


class OAuthInvalidCodeException(OAuthException):
    """Exception levée lorsque le code d'autorisation est invalide"""
    
    def __init__(self):
        super().__init__(
            detail="Le code d'autorisation OAuth2 est invalide ou a expiré",
            error_code="OAUTH_INVALID_CODE"
        )


class OAuthUserNotFoundException(OAuthException):
    """Exception levée lorsque l'utilisateur OAuth2 n'est pas trouvé"""
    
    def __init__(self):
        super().__init__(
            detail="Aucun compte OAuth2 trouvé pour cet utilisateur",
            error_code="OAUTH_USER_NOT_FOUND"
        )


class OAuthProviderException(OAuthException):
    """Exception levée lors d'une erreur du provider OAuth2"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            error_code="OAUTH_PROVIDER_ERROR"
        )


class OAuthAccountAlreadyLinkedException(OAuthException):
    """Exception levée lorsque le compte OAuth2 est déjà lié"""
    
    def __init__(self, provider: str):
        super().__init__(
            detail=f"Un compte {provider} est déjà lié à cet utilisateur",
            error_code="OAUTH_ACCOUNT_ALREADY_LINKED"
        )


class OAuthRegistrationRequiredException(HTTPException):
    """Exception levée lorsque l'inscription est requise"""
    
    def __init__(self, user_info: dict):
        super().__init__(
            status_code=status.HTTP_200_OK,  # 200 pour permettre la redirection côté client
            detail="Inscription requise pour compléter la connexion OAuth2",
            error_code="OAUTH_REGISTRATION_REQUIRED"
        )
        self.user_info = user_info


class OAuthEmailAlreadyExistsException(OAuthException):
    """Exception levée lorsque l'email OAuth2 existe déjà avec un autre compte"""
    
    def __init__(self, email: str):
        super().__init__(
            detail=f"L'email {email} est déjà utilisé par un autre compte",
            error_code="OAUTH_EMAIL_ALREADY_EXISTS"
        )


class OAuthScopePermissionException(OAuthException):
    """Exception levée lorsque les permissions OAuth2 sont insuffisantes"""
    
    def __init__(self, required_scope: str):
        super().__init__(
            detail=f"Permissions OAuth2 insuffisantes. Scope requis: {required_scope}",
            error_code="OAUTH_SCOPE_PERMISSION_ERROR"
        )


class OAuthRateLimitException(OAuthException):
    """Exception levée lors d'un dépassement du taux de tentatives OAuth2"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            detail="Trop de tentatives OAuth2 échouées. Veuillez réessayer plus tard",
            error_code="OAUTH_RATE_LIMIT"
        )
        self.retry_after = retry_after


class OAuthTokenExpiredException(OAuthException):
    """Exception levée lorsque le token OAuth2 a expiré"""
    
    def __init__(self):
        super().__init__(
            detail="Le token OAuth2 a expiré. Veuillez vous reconnecter",
            error_code="OAUTH_TOKEN_EXPIRED"
        )


class OAuthUnsupportedProviderException(OAuthException):
    """Exception levée lorsque le provider OAuth2 n'est pas supporté"""
    
    def __init__(self, provider: str):
        super().__init__(
            detail=f"Le provider OAuth2 '{provider}' n'est pas supporté",
            error_code="OAUTH_UNSUPPORTED_PROVIDER"
        )


class OAuthConfigurationException(OAuthException):
    """Exception levée lors d'une erreur de configuration OAuth2"""
    
    def __init__(self, provider: str):
        super().__init__(
            detail=f"Configuration OAuth2 manquante ou invalide pour le provider '{provider}'",
            error_code="OAUTH_CONFIGURATION_ERROR"
        )