# app/exceptions/business_exceptions.py
from fastapi import HTTPException, status
from datetime import datetime

class BusinessException(HTTPException):
    def __init__(self, code: str, message: str, details: str = None, status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Exceptions d'authentification
class InvalidCredentialsException(BusinessException):
    def __init__(self):
        super().__init__(
            code="AUTH_INVALID_CREDENTIALS",
            message="Identifiants invalides",
            details="Le nom d'utilisateur ou le mot de passe est incorrect",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class TokenExpiredException(BusinessException):
    def __init__(self):
        super().__init__(
            code="AUTH_TOKEN_EXPIRED",
            message="Token expiré",
            details="Votre session a expiré, veuillez vous reconnecter",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class TokenInvalidException(BusinessException):
    def __init__(self):
        super().__init__(
            code="AUTH_TOKEN_INVALID",
            message="Token invalide",
            details="Le token fourni n'est pas valide",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

# Exceptions utilisateur
class UserNotFoundException(BusinessException):
    def __init__(self, user_id: int = None):
        details = f"L'utilisateur avec l'ID {user_id} n'existe pas" if user_id else "Utilisateur non trouvé"
        super().__init__(
            code="USER_NOT_FOUND",
            message="Utilisateur non trouvé",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )

class UserEmailExistsException(BusinessException):
    def __init__(self, email: str):
        super().__init__(
            code="USER_EMAIL_EXISTS",
            message="Email déjà utilisé",
            details=f"Un compte avec l'email {email} existe déjà",
            status_code=status.HTTP_409_CONFLICT
        )

class UsernameExistsException(BusinessException):
    def __init__(self, username: str):
        super().__init__(
            code="USER_USERNAME_EXISTS",
            message="Nom d'utilisateur déjà pris",
            details=f"Le nom d'utilisateur {username} est déjà utilisé",
            status_code=status.HTTP_409_CONFLICT
        )

# Exceptions projet
class ProjectNotFoundException(BusinessException):
    def __init__(self, project_id: int = None):
        details = f"Le projet avec l'ID {project_id} n'existe pas" if project_id else "Projet non trouvé"
        super().__init__(
            code="PROJECT_NOT_FOUND",
            message="Projet non trouvé",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )

class ProjectAccessDeniedException(BusinessException):
    def __init__(self, project_id: int = None):
        details = f"Accès refusé au projet {project_id}" if project_id else "Accès au projet refusé"
        super().__init__(
            code="PROJECT_ACCESS_DENIED",
            message="Accès au projet refusé",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )

class ProjectAlreadyExistsException(BusinessException):
    def __init__(self, project_name: str):
        super().__init__(
            code="PROJECT_ALREADY_EXISTS",
            message="Projet déjà existant",
            details=f"Un projet avec le nom '{project_name}' existe déjà",
            status_code=status.HTTP_409_CONFLICT
        )

# Exceptions issue
class IssueNotFoundException(BusinessException):
    def __init__(self, issue_id: int = None):
        details = f"L'issue avec l'ID {issue_id} n'existe pas" if issue_id else "Issue non trouvée"
        super().__init__(
            code="ISSUE_NOT_FOUND",
            message="Issue non trouvée",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )

# Exceptions contributeur
class ContributorNotFoundException(BusinessException):
    def __init__(self, contributor_id: int = None):
        details = f"Le contributeur avec l'ID {contributor_id} n'existe pas" if contributor_id else "Contributeur non trouvé"
        super().__init__(
            code="CONTRIBUTOR_NOT_FOUND",
            message="Contributeur non trouvé",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )

class ContributorAlreadyExistsException(BusinessException):
    def __init__(self, user_id: int, project_id: int):
        super().__init__(
            code="CONTRIBUTOR_ALREADY_EXISTS",
            message="Contributeur déjà ajouté",
            details=f"L'utilisateur {user_id} est déjà contributeur du projet {project_id}",
            status_code=status.HTTP_409_CONFLICT
        )

# Exceptions commentaire
class CommentNotFoundException(BusinessException):
    def __init__(self, comment_id: int = None):
        details = f"Le commentaire avec l'ID {comment_id} n'existe pas" if comment_id else "Commentaire non trouvé"
        super().__init__(
            code="COMMENT_NOT_FOUND",
            message="Commentaire non trouvé",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )

# Exceptions de validation
class ValidationException(BusinessException):
    def __init__(self, field: str = None, message: str = "Erreur de validation"):
        details = f"Erreur de validation pour le champ '{field}'" if field else "Erreur de validation des données"
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )

# Exceptions de permissions
class InsufficientPermissionsException(BusinessException):
    def __init__(self, action: str = None):
        details = f"Permissions insuffisantes pour {action}" if action else "Permissions insuffisantes"
        super().__init__(
            code="INSUFFICIENT_PERMISSIONS",
            message="Permissions insuffisantes",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )