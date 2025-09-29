# app/utils/logger.py
import logging
import json
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Any


class StructuredJSONFormatter(logging.Formatter):
    """Formateur de logs en JSON structuré avec contexte enrichi"""
    
    def format(self, record):
        # Structure de base du log
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread_name": record.threadName,
        }
        
        # Ajout des données supplémentaires structurées
        if hasattr(record, 'extra_data') and record.extra_data:
            log_entry.update(record.extra_data)
            
        # Ajout des informations d'exception
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Filtrage des données sensibles
        log_entry = self._filter_sensitive_data(log_entry)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)
    
    def _filter_sensitive_data(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Filtre les données sensibles des logs"""
        sensitive_fields = [
            'password', 'token', 'secret', 'authorization',
            'api_key', 'credit_card', 'ssn', 'phone'
        ]
        
        for field in sensitive_fields:
            if field in log_entry:
                log_entry[field] = "***FILTERED***"
                
        return log_entry


class ContextFilter(logging.Filter):
    """Filtre qui ajoute un contexte commun à tous les logs"""
    
    def __init__(self, service_name: str, environment: str):
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        
    def filter(self, record):
        if not hasattr(record, 'extra_data'):
            record.extra_data = {}
            
        record.extra_data.update({
            "service": self.service_name,
            "environment": self.environment,
        })
        return True


class PerformanceFilter(logging.Filter):
    """Filtre pour les logs de performance"""
    
    def filter(self, record):
        # Ne loguer que les messages de performance si le niveau est INFO ou supérieur
        if hasattr(record, 'extra_data') and record.extra_data.get('category') == 'performance':
            return record.levelno >= logging.INFO
        return True


def setup_logging(
    level: str = "INFO",
    environment: str = "development",
    service_name: str = "issue-tracking-api",
    log_directory: str = "logs"
):
    """Configure le système de logging avec des options avancées"""
    
    # Création du répertoire de logs si nécessaire
    os.makedirs(log_directory, exist_ok=True)
    
    # Configuration du logger racine
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Suppression des handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Filtre de contexte
    context_filter = ContextFilter(service_name, environment)
    
    # Handler console pour le développement
    if environment == "development":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredJSONFormatter())
        console_handler.addFilter(context_filter)
        logger.addHandler(console_handler)
    
    # Handler de fichier principal avec rotation
    main_handler = RotatingFileHandler(
        filename=os.path.join(log_directory, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_handler.setFormatter(StructuredJSONFormatter())
    main_handler.addFilter(context_filter)
    logger.addHandler(main_handler)
    
    # Handler d'erreurs avec rotation temporelle
    error_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_directory, "error.log"),
        when='midnight',
        interval=1,
        backupCount=30,  # 30 jours
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredJSONFormatter())
    error_handler.addFilter(context_filter)
    logger.addHandler(error_handler)
    
    # Handler pour les logs de performance
    performance_handler = RotatingFileHandler(
        filename=os.path.join(log_directory, "performance.log"),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.addFilter(PerformanceFilter())
    performance_handler.setFormatter(StructuredJSONFormatter())
    performance_handler.addFilter(context_filter)
    logger.addHandler(performance_handler)
    
    # Configuration des loggers tiers pour éviter le bruit
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)


# Fonctions utilitaires pour le logging structuré
def log_request(request, extra_data: Optional[Dict[str, Any]] = None):
    """Log structuré des requêtes HTTP"""
    logger = logging.getLogger("http.request")
    
    extra = {
        "category": "http",
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_type": request.headers.get("content-type"),
        "content_length": request.headers.get("content-length"),
    }
    
    if extra_data:
        extra.update(extra_data)
    
    logger.info(f"HTTP Request: {request.method} {request.url.path}",
                extra={"extra_data": extra})


def log_response(request, response, extra_data: Optional[Dict[str, Any]] = None):
    """Log structuré des réponses HTTP"""
    logger = logging.getLogger("http.response")
    
    extra = {
        "category": "http",
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "status_code": response.status_code,
        "client_ip": request.client.host if request.client else "unknown",
        "response_size": len(response.body) if hasattr(response, 'body') else 0,
    }
    
    if extra_data:
        extra.update(extra_data)
    
    log_level = logging.INFO if response.status_code < 400 else logging.WARNING
    
    logger.log(log_level, f"HTTP Response: {response.status_code} {request.method} {request.url.path}",
               extra={"extra_data": extra})


def log_error(error_message: str,
              exc_info: Optional[tuple] = None,
              extra_data: Optional[Dict[str, Any]] = None,
              error_code: Optional[str] = None):
    """Log structuré des erreurs"""
    logger = logging.getLogger("error")
    
    extra = {
        "category": "error",
        "error_code": error_code,
    }
    
    if extra_data:
        extra.update(extra_data)
    
    logger.error(error_message, exc_info=exc_info, extra={"extra_data": extra})


def log_business_event(event_type: str,
                       message: str,
                       extra_data: Optional[Dict[str, Any]] = None,
                       user_id: Optional[int] = None):
    """Log structuré des événements métier"""
    logger = logging.getLogger("business")
    
    extra = {
        "category": "business",
        "event_type": event_type,
        "user_id": user_id,
    }
    
    if extra_data:
        extra.update(extra_data)
    
    logger.info(message, extra={"extra_data": extra})


def log_performance(operation: str,
                    duration_ms: float,
                    extra_data: Optional[Dict[str, Any]] = None):
    """Log structuré des métriques de performance"""
    logger = logging.getLogger("performance")
    
    extra = {
        "category": "performance",
        "operation": operation,
        "duration_ms": duration_ms,
    }
    
    if extra_data:
        extra.update(extra_data)
    
    logger.info(f"Performance: {operation} took {duration_ms:.2f}ms",
                extra={"extra_data": extra})


def log_security_event(event_type: str,
                       message: str,
                       extra_data: Optional[Dict[str, Any]] = None,
                       severity: str = "medium"):
    """Log structuré des événements de sécurité"""
    logger = logging.getLogger("security")
    
    extra = {
        "category": "security",
        "event_type": event_type,
        "severity": severity,
    }
    
    if extra_data:
        extra.update(extra_data)
    
    log_level = {
        "low": logging.INFO,
        "medium": logging.WARNING,
        "high": logging.ERROR
    }.get(severity, logging.WARNING)
    
    logger.log(log_level, message, extra={"extra_data": extra})


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger nommé avec le contexte par défaut"""
    return logging.getLogger(name)