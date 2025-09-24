# app/middleware/exception_handler.py
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.response_schemas import ErrorResponse, ErrorDetail, Metadata
from datetime import datetime

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    # Log de l'erreur
    logger.error(
        f"Erreur sur {request.method} {request.url}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    if isinstance(exc, HTTPException):
        # Gestion des exceptions HTTP personnalisées
        error_detail = exc.detail
        
        # Si l'exception a un détail structuré, on l'utilise
        if isinstance(error_detail, dict) and "code" in error_detail:
            error_code = error_detail.get("code", "HTTP_ERROR")
            error_message = error_detail.get("message", str(exc))
            error_details = error_detail.get("details")
        else:
            error_code = "HTTP_ERROR"
            error_message = str(error_detail)
            error_details = None
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=error_code,
                    message=error_message,
                    details=error_details,
                    timestamp=datetime.utcnow()
                ),
                metadata=Metadata(timestamp=datetime.utcnow())
            ).dict()
        )
    else:
        # Erreur serveur inattendue
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="Erreur interne du serveur",
                    details="Une erreur inattendue s'est produite",
                    timestamp=datetime.utcnow()
                ),
                metadata=Metadata(timestamp=datetime.utcnow())
            ).dict()
        )