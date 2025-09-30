# backend/app/schemas/session_schema.py
"""
Schémas Pydantic pour la gestion des sessions
Validation des données d'entrée et de sortie pour les API de sessions
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SessionInfo(BaseModel):
    """Informations d'une session utilisateur"""
    
    id: Optional[int] = None
    ip_address: str
    device_type: Optional[str] = None
    browser: Optional[str] = None
    platform: Optional[str] = None
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_mobile: bool = False
    
    class Config:
        from_attributes = True


class ActiveSessionsResponse(BaseModel):
    """Réponse pour la liste des sessions actives"""
    
    sessions: List[SessionInfo]
    total_active: int
    
    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Réponse générique pour les opérations sur les sessions"""
    
    message: str
    session_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class LoginHistoryInfo(BaseModel):
    """Informations d'un historique de connexion"""
    
    id: int
    login_type: str
    provider: Optional[str] = None
    ip_address: str
    location: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = None
    login_at: datetime
    logout_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    class Config:
        from_attributes = True


class LoginHistoryResponse(BaseModel):
    """Réponse pour l'historique des connexions"""
    
    history: List[LoginHistoryInfo]
    total_entries: int
    
    class Config:
        from_attributes = True


class SecurityEventInfo(BaseModel):
    """Informations d'un événement de sécurité"""
    
    id: int
    event_type: str
    severity: str
    description: str
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SecurityEventsResponse(BaseModel):
    """Réponse pour les événements de sécurité"""
    
    events: List[SecurityEventInfo]
    total_events: int
    
    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """Requête pour rafraîchir une session"""
    
    refresh_token: str
    
    class Config:
        from_attributes = True


class CreateSessionRequest(BaseModel):
    """Requête pour créer une nouvelle session"""
    
    device_type: str = "web"
    is_mobile: bool = False
    session_duration_hours: int = 24
    
    class Config:
        from_attributes = True


class LogoutRequest(BaseModel):
    """Requête pour déconnecter une session"""
    
    session_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class SessionStatsResponse(BaseModel):
    """Statistiques des sessions"""
    
    total_sessions: int
    active_sessions: int
    expired_sessions: int
    average_session_duration_minutes: float
    most_used_device: Optional[str] = None
    most_common_browser: Optional[str] = None
    
    class Config:
        from_attributes = True


class SecurityAlertRequest(BaseModel):
    """Requête pour créer une alerte de sécurité"""
    
    event_type: str
    severity: str
    description: str
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True


class UserAgentInfo(BaseModel):
    """Informations extraites du User-Agent"""
    
    device_type: str
    browser: str
    platform: str
    is_mobile: bool
    
    class Config:
        from_attributes = True