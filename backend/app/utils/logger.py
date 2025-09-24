# app/utils/logger.py
import logging
import json
from datetime import datetime
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Ajout des données supplémentaires si présentes
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        # Ajout de l'exception si présente
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    # Configuration du logger racine
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Suppression des handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler console avec format JSON
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # Handler fichier
    file_handler = logging.FileHandler("app.log", encoding='utf-8')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Configuration spécifique pour les logs d'erreur
    error_handler = logging.FileHandler("error.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    logger.addHandler(error_handler)

# Fonctions utilitaires pour le logging
def log_request(request, extra_data=None):
    logger = logging.getLogger("request")
    extra = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    if extra_data:
        extra.update(extra_data)
    
    logger.info(f"Requête {request.method} {request.url}", extra={"extra_data": extra})

def log_response(request, response, extra_data=None):
    logger = logging.getLogger("response")
    extra = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "client_ip": request.client.host if request.client else "unknown",
    }
    if extra_data:
        extra.update(extra_data)
    
    logger.info(f"Réponse {request.method} {request.url} - {response.status_code}", 
                extra={"extra_data": extra})

def log_error(error_message, exc_info=None, extra_data=None):
    logger = logging.getLogger("error")
    extra = {}
    if extra_data:
        extra.update(extra_data)
    
    logger.error(error_message, exc_info=exc_info, extra={"extra_data": extra})

def log_business_event(event_type, message, extra_data=None):
    logger = logging.getLogger("business")
    extra = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    if extra_data:
        extra.update(extra_data)
    
    logger.info(message, extra={"extra_data": extra})