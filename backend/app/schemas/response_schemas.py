# app/schemas/response_schemas.py
from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime

class Metadata(BaseModel):
    timestamp: datetime
    version: str = "1.0.0"
    request_id: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    metadata: Metadata

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    metadata: Metadata