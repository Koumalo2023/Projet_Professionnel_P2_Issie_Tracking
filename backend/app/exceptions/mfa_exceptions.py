# app/exceptions/mfa_exceptions.py
"""
Exceptions spécifiques à l'authentification multi-facteurs (MFA)
"""

from fastapi import status
from app.exceptions.http_exceptions import HTTPException


class MFAException(HTTPException):
    """Exception de base pour les erreurs MFA"""
    
    def __init__(self, detail: str, error_code: str = "MFA_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class MFAAlreadyEnabledException(MFAException):
    """Exception levée lorsque le MFA est déjà activé"""
    
    def __init__(self):
        super().__init__(
            detail="L'authentification multi-facteurs est déjà activée pour cet utilisateur",
            error_code="MFA_ALREADY_ENABLED"
        )


class MFANotEnabledException(MFAException):
    """Exception levée lorsque le MFA n'est pas activé"""
    
    def __init__(self, detail: str = "L'authentification multi-facteurs n'est pas activée"):
        super().__init__(
            detail=detail,
            error_code="MFA_NOT_ENABLED"
        )


class MFAInvalidCodeException(MFAException):
    """Exception levée lorsque le code MFA est invalide"""
    
    def __init__(self):
        super().__init__(
            detail="Le code d'authentification est invalide ou a expiré",
            error_code="MFA_INVALID_CODE"
        )


class MFAInvalidRecoveryCodeException(MFAException):
    """Exception levée lorsque le code de récupération est invalide"""
    
    def __init__(self):
        super().__init__(
            detail="Le code de récupération est invalide ou a déjà été utilisé",
            error_code="MFA_INVALID_RECOVERY_CODE"
        )


class MFARateLimitException(MFAException):
    """Exception levée lors d'un dépassement du taux de tentatives"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            detail="Trop de tentatives échouées. Veuillez réessayer plus tard",
            error_code="MFA_RATE_LIMIT"
        )
        self.retry_after = retry_after


class MFASetupRequiredException(HTTPException):
    """Exception levée lorsque la configuration MFA est requise"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Configuration MFA requise pour accéder à cette ressource",
            error_code="MFA_SETUP_REQUIRED"
        )


class MFAVerificationRequiredException(HTTPException):
    """Exception levée lorsque la vérification MFA est requise"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vérification MFA requise pour compléter l'authentification",
            error_code="MFA_VERIFICATION_REQUIRED"
        )


class MFANotConfiguredException(MFAException):
    """Exception levée lorsque le MFA n'est pas configuré"""
    
    def __init__(self):
        super().__init__(
            detail="L'authentification multi-facteurs n'est pas configurée pour cet utilisateur",
            error_code="MFA_NOT_CONFIGURED"
        )


class MFAExpiredCodeException(MFAException):
    """Exception levée lorsque le code MFA a expiré"""
    
    def __init__(self):
        super().__init__(
            detail="Le code d'authentification a expiré. Veuillez en générer un nouveau",
            error_code="MFA_EXPIRED_CODE"
        )


class MFABackupCodeLimitException(MFAException):
    """Exception levée lorsque le nombre maximum de codes de secours est atteint"""
    
    def __init__(self):
        super().__init__(
            detail="Nombre maximum de codes de secours générés. Veuillez utiliser les codes existants",
            error_code="MFA_BACKUP_CODE_LIMIT"
        )