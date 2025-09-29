# app/exceptions/business_exceptions.py
from fastapi import status
from datetime import datetime
from typing import Optional, Dict, Any
from .http_exceptions import BaseHTTPException


class BusinessException(BaseHTTPException):
    """Classe de base pour toutes les exceptions métier"""
    def __init__(self, 
                 code: str, 
                 message: str, 
                 details: Optional[str] = None,
                 status_code: int = status.HTTP_400_BAD_REQUEST,
                 extra_data: Optional[Dict[str, Any]] = None):
        
        super().__init__(
            status_code=status_code,
            code=code,
            message=message,
            details=details,
            extra_data=extra_data
        )


# Exceptions d'authentification
class AuthenticationException(BusinessException):
    def __init__(self,
                 message: str = "Authentication failed",
                 details: Optional[str] = None,
                 code: str = "AUTH_ERROR"):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidCredentialsException(AuthenticationException):
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid credentials",
            details=details or "The provided username or password is incorrect"
        )


class TokenExpiredException(AuthenticationException):
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="Token expired",
            details=details or "The authentication token has expired",
            code="AUTH_TOKEN_EXPIRED"
        )


class InvalidTokenException(AuthenticationException):
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="Invalid token",
            details=details or "The authentication token is invalid",
            code="AUTH_TOKEN_INVALID"
        )


# Exceptions utilisateur
class UserNotFoundException(BusinessException):
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        details = None
        extra_data = {}
        
        if user_id:
            details = f"User with ID {user_id} not found"
            extra_data["user_id"] = user_id
        elif email:
            details = f"User with email {email} not found"
            extra_data["email"] = email
            
        super().__init__(
            code="USER_NOT_FOUND",
            message="User not found",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND,
            extra_data=extra_data
        )


class UserAlreadyExistsException(BusinessException):
    def __init__(self, email: Optional[str] = None, username: Optional[str] = None):
        details = None
        extra_data = {}
        
        if email:
            details = f"User with email {email} already exists"
            extra_data["email"] = email
        elif username:
            details = f"User with username {username} already exists"
            extra_data["username"] = username
            
        super().__init__(
            code="USER_ALREADY_EXISTS",
            message="User already exists",
            details=details,
            status_code=status.HTTP_409_CONFLICT,
            extra_data=extra_data
        )


class UserInactiveException(BusinessException):
    def __init__(self, user_id: Optional[int] = None):
        details = "User account is inactive"
        extra_data = {}
        
        if user_id:
            extra_data["user_id"] = user_id
            
        super().__init__(
            code="USER_INACTIVE",
            message="User account is inactive",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data=extra_data
        )


# Exceptions projet
class ProjectNotFoundException(BusinessException):
    def __init__(self, project_id: int):
        super().__init__(
            code="PROJECT_NOT_FOUND",
            message="Project not found",
            details=f"Project with ID {project_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            extra_data={"project_id": project_id}
        )


class ProjectAccessDeniedException(BusinessException):
    def __init__(self, project_id: int, user_id: Optional[int] = None):
        details = f"Access denied to project {project_id}"
        extra_data = {"project_id": project_id}
        
        if user_id:
            extra_data["user_id"] = user_id
            
        super().__init__(
            code="PROJECT_ACCESS_DENIED",
            message="Project access denied",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data=extra_data
        )


class ProjectAlreadyExistsException(BusinessException):
    def __init__(self, project_name: str):
        super().__init__(
            code="PROJECT_ALREADY_EXISTS",
            message="Project already exists",
            details=f"Project with name '{project_name}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            extra_data={"project_name": project_name}
        )


# Exceptions issue
class IssueNotFoundException(BusinessException):
    def __init__(self, issue_id: int):
        super().__init__(
            code="ISSUE_NOT_FOUND",
            message="Issue not found",
            details=f"Issue with ID {issue_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            extra_data={"issue_id": issue_id}
        )


class IssueAccessDeniedException(BusinessException):
    def __init__(self, issue_id: int, user_id: Optional[int] = None):
        details = f"Access denied to issue {issue_id}"
        extra_data = {"issue_id": issue_id}
        
        if user_id:
            extra_data["user_id"] = user_id
            
        super().__init__(
            code="ISSUE_ACCESS_DENIED",
            message="Issue access denied",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data=extra_data
        )


# Exceptions commentaire
class CommentNotFoundException(BusinessException):
    def __init__(self, comment_id: int):
        super().__init__(
            code="COMMENT_NOT_FOUND",
            message="Comment not found",
            details=f"Comment with ID {comment_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            extra_data={"comment_id": comment_id}
        )


class CommentAccessDeniedException(BusinessException):
    def __init__(self, comment_id: int, user_id: Optional[int] = None):
        details = f"Access denied to comment {comment_id}"
        extra_data = {"comment_id": comment_id}
        
        if user_id:
            extra_data["user_id"] = user_id
            
        super().__init__(
            code="COMMENT_ACCESS_DENIED",
            message="Comment access denied",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data=extra_data
        )


# Exceptions contributeur
class ContributorNotFoundException(BusinessException):
    def __init__(self, contributor_id: int):
        super().__init__(
            code="CONTRIBUTOR_NOT_FOUND",
            message="Contributor not found",
            details=f"Contributor with ID {contributor_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            extra_data={"contributor_id": contributor_id}
        )


class ContributorAlreadyExistsException(BusinessException):
    def __init__(self, project_id: int, user_id: int):
        super().__init__(
            code="CONTRIBUTOR_ALREADY_EXISTS",
            message="Contributor already exists",
            details=f"User {user_id} is already a contributor to project {project_id}",
            status_code=status.HTTP_409_CONFLICT,
            extra_data={"project_id": project_id, "user_id": user_id}
        )


# Exceptions permissions
class PermissionDeniedException(BusinessException):
    def __init__(self, 
                 required_permission: str, 
                 resource_type: str,
                 resource_id: Optional[int] = None):
        
        details = f"Permission '{required_permission}' required for {resource_type}"
        extra_data = {
            "required_permission": required_permission,
            "resource_type": resource_type
        }
        
        if resource_id:
            details += f" with ID {resource_id}"
            extra_data["resource_id"] = resource_id
            
        super().__init__(
            code="PERMISSION_DENIED",
            message="Permission denied",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data=extra_data
        )


class InsufficientPermissionsException(BusinessException):
    def __init__(self, 
                 required_permissions: list, 
                 user_permissions: list,
                 resource_type: str):
        
        super().__init__(
            code="INSUFFICIENT_PERMISSIONS",
            message="Insufficient permissions",
            details=f"Required permissions: {required_permissions} for {resource_type}",
            status_code=status.HTTP_403_FORBIDDEN,
            extra_data={
                "required_permissions": required_permissions,
                "user_permissions": user_permissions,
                "resource_type": resource_type
            }
        )


# Exceptions de validation
class ValidationException(BusinessException):
    def __init__(self, 
                 message: str = "Validation error", 
                 details: Optional[str] = None,
                 validation_errors: Optional[list] = None):
        
        extra_data = {}
        if validation_errors:
            extra_data["validation_errors"] = validation_errors
            
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            extra_data=extra_data
        )


# Exceptions de base de données
class DatabaseException(BusinessException):
    def __init__(self, 
                 message: str = "Database error", 
                 details: Optional[str] = None,
                 operation: Optional[str] = None):
        
        extra_data = {}
        if operation:
            extra_data["operation"] = operation
            
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            extra_data=extra_data
        )


# Exceptions de service externe
class ExternalServiceException(BusinessException):
    def __init__(self, 
                 service_name: str, 
                 message: str = "External service error",
                 details: Optional[str] = None):
        
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=message,
            details=details or f"Error communicating with {service_name}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            extra_data={"service_name": service_name}
        )