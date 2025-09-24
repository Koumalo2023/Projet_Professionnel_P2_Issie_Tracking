# app/middleware/logging.py
import logging
from app.utils.logger import log_request, log_response

async def log_requests(request, call_next):
    # Log de la requête
    log_request(request)
    
    # Exécution de la requête
    response = await call_next(request)
    
    # Log de la réponse
    log_response(request, response)
    
    return response