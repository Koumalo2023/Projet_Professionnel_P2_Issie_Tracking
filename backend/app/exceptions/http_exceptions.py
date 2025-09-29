# api/app/exceptions/http_exceptions.py
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any


class BaseHTTPException(HTTPException):
    """Classe de base pour toutes les exceptions HTTP personnalisées"""
    def __init__(self,
                 status_code: int,
                 code: str,
                 message: str,
                 details: Optional[str] = None,
                 extra_data: Optional[Dict[str, Any]] = None):
        
        error_detail = {
            "code": code,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if extra_data:
            error_detail.update(extra_data)
            
        super().__init__(status_code=status_code, detail=error_detail)


class NotFoundException(BaseHTTPException):
    def __init__(self,
                 message: str = "Resource not found",
                 details: Optional[str] = None,
                 resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None):
        
        extra_data = {}
        if resource_type:
            extra_data["resource_type"] = resource_type
        if resource_id:
            extra_data["resource_id"] = resource_id
            
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            details=details,
            extra_data=extra_data
        )


class UnauthorizedException(BaseHTTPException):
    def __init__(self,
                 message: str = "Authentication required",
                 details: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
            details=details
        )


class ForbiddenException(BaseHTTPException):
    def __init__(self,
                 message: str = "Access forbidden",
                 details: Optional[str] = None,
                 required_permission: Optional[str] = None):
        
        extra_data = {}
        if required_permission:
            extra_data["required_permission"] = required_permission
            
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
            details=details,
            extra_data=extra_data
        )


class BadRequestException(BaseHTTPException):
    def __init__(self,
                 message: str = "Bad request",
                 details: Optional[str] = None,
                 validation_errors: Optional[list] = None):
        
        extra_data = {}
        if validation_errors:
            extra_data["validation_errors"] = validation_errors
            
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
            message=message,
            details=details,
            extra_data=extra_data
        )


class ConflictException(BaseHTTPException):
    def __init__(self,
                 message: str = "Resource conflict",
                 details: Optional[str] = None,
                 conflicting_field: Optional[str] = None):
        
        extra_data = {}
        if conflicting_field:
            extra_data["conflicting_field"] = conflicting_field
            
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
            details=details,
            extra_data=extra_data
        )


class ValidationException(BaseHTTPException):
    def __init__(self,
                 message: str = "Validation error",
                 details: Optional[str] = None,
                 validation_errors: Optional[list] = None):
        
        extra_data = {}
        if validation_errors:
            extra_data["validation_errors"] = validation_errors
            
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            extra_data=extra_data
        )


class InternalServerErrorException(BaseHTTPException):
    def __init__(self,
                 message: str = "Internal server error",
                 details: Optional[str] = None,
                 error_id: Optional[str] = None):
        
        extra_data = {}
        if error_id:
            extra_data["error_id"] = error_id
            
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message=message,
            details=details,
            extra_data=extra_data
        )


class ServiceUnavailableException(BaseHTTPException):
    def __init__(self,
                 message: str = "Service temporarily unavailable",
                 details: Optional[str] = None,
                 retry_after: Optional[int] = None):
        
        extra_data = {}
        if retry_after:
            extra_data["retry_after"] = retry_after
            
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="SERVICE_UNAVAILABLE",
            message=message,
            details=details,
            extra_data=extra_data
        )


class TooManyRequestsException(BaseHTTPException):
    def __init__(self,
                 message: str = "Too many requests",
                 details: Optional[str] = None,
                 retry_after: Optional[int] = None):
        
        extra_data = {}
        if retry_after:
            extra_data["retry_after"] = retry_after
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            details=details,
            extra_data=extra_data
        )