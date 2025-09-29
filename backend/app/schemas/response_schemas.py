# app/schemas/response_schemas.py
from pydantic import BaseModel
from typing import Any, Optional, Dict, List
from datetime import datetime


class Metadata(BaseModel):
    """Schéma pour les métadonnées de réponse"""
    timestamp: datetime
    version: str = "1.0.0"
    request_id: Optional[str] = None
    pagination: Optional[Dict[str, Any]] = None


class ErrorDetail(BaseModel):
    """Schéma pour les détails d'erreur"""
    code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime
    field: Optional[str] = None
    value: Optional[Any] = None


class SuccessResponse(BaseModel):
    """Schéma de réponse standard pour les succès"""
    success: bool = True
    data: Any
    metadata: Metadata


class ErrorResponse(BaseModel):
    """Schéma de réponse standard pour les erreurs"""
    success: bool = False
    error: ErrorDetail
    metadata: Metadata


class PaginationInfo(BaseModel):
    """Informations de pagination"""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    """Schéma pour les réponses paginées"""
    success: bool = True
    data: List[Any]
    pagination: PaginationInfo
    metadata: Metadata


class ValidationErrorDetail(BaseModel):
    """Détails d'erreur de validation"""
    field: str
    message: str
    value: Optional[Any] = None
    type: str


class ValidationErrorResponse(BaseModel):
    """Schéma pour les erreurs de validation"""
    success: bool = False
    error: ErrorDetail
    validation_errors: List[ValidationErrorDetail]
    metadata: Metadata