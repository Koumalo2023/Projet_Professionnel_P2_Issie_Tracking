# app/middleware/exception_handler.py
import logging
import uuid
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.schemas.response_schemas import (
    ErrorResponse,
    ErrorDetail,
    Metadata,
    ValidationErrorResponse,
    ValidationErrorDetail
)
from app.exceptions.business_exceptions import BusinessException
from app.exceptions.http_exceptions import BaseHTTPException
from datetime import datetime

logger = logging.getLogger(__name__)


def _generate_request_id() -> str:
    """Génère un identifiant unique pour la requête"""
    return str(uuid.uuid4())


def _extract_error_info(exc: Exception) -> tuple:
    """Extrait les informations d'erreur de l'exception"""
    if isinstance(exc, (BaseHTTPException, BusinessException)):
        # Nos exceptions personnalisées ont déjà un format structuré
        error_detail = exc.detail
        return (
            error_detail.get("code", "UNKNOWN_ERROR"),
            error_detail.get("message", str(exc)),
            error_detail.get("details"),
            error_detail.get("extra_data", {})
        )
    elif isinstance(exc, HTTPException):
        # Exceptions HTTP FastAPI standard
        return "HTTP_ERROR", str(exc.detail), None, {}
    else:
        # Erreurs génériques
        return "INTERNAL_SERVER_ERROR", "Internal server error", str(exc), {}


def _log_exception(request: Request, exc: Exception, request_id: str):
    """Journalise l'exception avec un contexte détaillé"""
    error_code, error_message, error_details, extra_data = _extract_error_info(exc)
    
    log_context = {
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "error_type": type(exc).__name__,
        "error_code": error_code,
        "error_message": error_message,
        "error_details": error_details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Ajoute les données supplémentaires de l'exception
    if extra_data:
        log_context.update(extra_data)
    
    # Log avec le niveau approprié
    if isinstance(exc, (BusinessException, BaseHTTPException)):
        # Erreurs métier attendues - niveau WARNING
        logger.warning(f"Business exception: {error_code}", extra=log_context)
    elif isinstance(exc, HTTPException) and exc.status_code < 500:
        # Erreurs client - niveau WARNING
        logger.warning(f"Client error: {error_code}", extra=log_context)
    else:
        # Erreurs serveur - niveau ERROR
        logger.error(f"Server error: {error_code}", extra=log_context)


async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global d'exceptions pour FastAPI"""
    request_id = _generate_request_id()
    
    # Journalisation de l'erreur
    _log_exception(request, exc, request_id)
    
    # Gestion des erreurs de validation Pydantic
    if isinstance(exc, RequestValidationError):
        return await _handle_validation_error(request, exc, request_id)
    
    # Gestion des erreurs SQLAlchemy
    if isinstance(exc, SQLAlchemyError):
        return await _handle_database_error(request, exc, request_id)
    
    # Gestion des exceptions HTTP personnalisées et standard
    if isinstance(exc, HTTPException):
        return await _handle_http_exception(request, exc, request_id)
    
    # Gestion des erreurs génériques
    return await _handle_generic_error(request, exc, request_id)


async def _handle_validation_error(request: Request, exc: RequestValidationError, request_id: str):
    """Gestion des erreurs de validation Pydantic"""
    validation_errors = []
    
    for error in exc.errors():
        validation_errors.append(ValidationErrorDetail(
            field=" -> ".join(str(loc) for loc in error.get("loc", [])),
            message=error.get("msg", "Validation error"),
            type=error.get("type", "unknown")
        ))
    
    error_response = ValidationErrorResponse(
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="Validation error",
            details="One or more validation errors occurred",
            timestamp=datetime.utcnow()
        ),
        validation_errors=validation_errors,
        metadata=Metadata(
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    )
    
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(error_response.dict())
    )


async def _handle_database_error(request: Request, exc: SQLAlchemyError, request_id: str):
    """Gestion des erreurs de base de données"""
    # Ne pas exposer les détails de la base de données en production
    error_detail = "Database operation failed"
    
    # En développement, on peut logger plus de détails
    if logger.level <= logging.DEBUG:
        error_detail = str(exc)
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="DATABASE_ERROR",
            message="Database error",
            details=error_detail,
            timestamp=datetime.utcnow()
        ),
        metadata=Metadata(
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    )
    
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response.dict())
    )


async def _handle_http_exception(request: Request, exc: HTTPException, request_id: str):
    """Gestion des exceptions HTTP"""
    error_code, error_message, error_details, extra_data = _extract_error_info(exc)
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=error_message,
            details=error_details,
            timestamp=datetime.utcnow()
        ),
        metadata=Metadata(
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response.dict())
    )


async def _handle_generic_error(request: Request, exc: Exception, request_id: str):
    """Gestion des erreurs génériques non capturées"""
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="Internal server error",
            details="An unexpected error occurred",
            timestamp=datetime.utcnow()
        ),
        metadata=Metadata(
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    )
    
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response.dict())
    )