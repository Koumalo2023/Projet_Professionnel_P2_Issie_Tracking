# backend/app/services/session_service.py
"""
Service pour la gestion des sessions utilisateur
Suivi des connexions actives, historique des sessions et événements de sécurité
"""

import secrets
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.session import UserSession, LoginHistory, SecurityEvent
from app.models.user import User
from app.utils.logger import get_logger
from app.exceptions.session_exceptions import (
    SessionNotFoundException,
    SessionExpiredException,
    TooManyActiveSessionsException,
    InvalidSessionException
)

logger = get_logger(__name__)


class SessionService:
    """Service de gestion des sessions utilisateur"""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_active_sessions = 5  # Nombre maximum de sessions actives par utilisateur
    
    def create_session(self, user: User, ip_address: str, user_agent: Optional[str] = None,
                      device_type: str = "web", is_mobile: bool = False,
                      session_duration_hours: int = 24) -> UserSession:
        """
        Crée une nouvelle session utilisateur
        
        Args:
            user: Utilisateur concerné
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            device_type: Type de device (web, mobile, tablet)
            is_mobile: Si c'est un appareil mobile
            session_duration_hours: Durée de la session en heures
            
        Returns:
            Nouvelle session créée
        """
        # Vérifie le nombre de sessions actives
        active_sessions = self.get_active_sessions(user)
        if len(active_sessions) >= self.max_active_sessions:
            raise TooManyActiveSessionsException(self.max_active_sessions)
        
        # Génère des tokens uniques
        session_token = self._generate_session_token()
        refresh_token = self._generate_refresh_token()
        csrf_token = secrets.token_urlsafe(32)
        
        # Calcule la date d'expiration
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=session_duration_hours)
        
        # Détecte le navigateur et la plateforme
        browser, platform = self._parse_user_agent(user_agent)
        
        # Crée la session
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            platform=platform,
            is_mobile=is_mobile,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            is_active=True
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Journalise la création de session
        self._log_security_event(
            user_id=user.id,
            event_type="session_created",
            severity="low",
            description=f"Nouvelle session créée depuis {ip_address}",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session.id
        )
        
        logger.info(f"Session créée pour l'utilisateur {user.id} depuis {ip_address}")
        
        return session
    
    def validate_session(self, session_token: str, ip_address: str, 
                        user_agent: Optional[str] = None) -> UserSession:
        """
        Valide une session et met à jour l'activité
        
        Args:
            session_token: Token de session à valider
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            
        Returns:
            Session validée
            
        Raises:
            SessionNotFoundException: Si la session n'existe pas
            SessionExpiredException: Si la session est expirée
            InvalidSessionException: Si la session est inactive
        """
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if not session:
            raise SessionNotFoundException()
        
        if not session.is_active:
            raise InvalidSessionException("Session inactive")
        
        if session.is_expired():
            # Marque la session comme inactive
            session.is_active = False
            self.db.commit()
            
            # Journalise l'expiration
            self._log_security_event(
                user_id=session.user_id,
                event_type="session_expired",
                severity="low",
                description="Session expirée",
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session.id
            )
            
            raise SessionExpiredException()
        
        # Met à jour la dernière activité
        session.update_activity()
        self.db.commit()
        
        return session
    
    def refresh_session(self, refresh_token: str, ip_address: str,
                       user_agent: Optional[str] = None) -> UserSession:
        """
        Rafraîchit une session avec un nouveau token
        
        Args:
            refresh_token: Token de rafraîchissement
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            
        Returns:
            Session rafraîchie
        """
        session = self.db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise SessionNotFoundException()
        
        if session.is_expired():
            session.is_active = False
            self.db.commit()
            raise SessionExpiredException()
        
        # Génère de nouveaux tokens
        new_session_token = self._generate_session_token()
        new_refresh_token = self._generate_refresh_token()
        new_csrf_token = secrets.token_urlsafe(32)
        
        # Met à jour les tokens
        old_session_token = session.session_token
        session.session_token = new_session_token
        session.refresh_token = new_refresh_token
        session.csrf_token = new_csrf_token
        session.last_activity = datetime.utcnow()
        session.expires_at = datetime.utcnow() + timedelta(hours=24)
        
        self.db.commit()
        
        # Journalise le rafraîchissement
        self._log_security_event(
            user_id=session.user_id,
            event_type="session_refreshed",
            severity="low",
            description=f"Session rafraîchie - ancien token: {old_session_token[:10]}...",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session.id
        )
        
        logger.info(f"Session rafraîchie pour l'utilisateur {session.user_id}")
        
        return session
    
    def logout_session(self, session_token: str, ip_address: str,
                      user_agent: Optional[str] = None) -> bool:
        """
        Déconnecte une session spécifique
        
        Args:
            session_token: Token de session à déconnecter
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            
        Returns:
            True si la déconnexion a réussi
        """
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if not session:
            raise SessionNotFoundException()
        
        # Marque la session comme inactive
        session.is_active = False
        self.db.commit()
        
        # Met à jour l'historique de connexion
        self._update_login_history(session, logout_time=datetime.utcnow())
        
        # Journalise la déconnexion
        self._log_security_event(
            user_id=session.user_id,
            event_type="session_logout",
            severity="low",
            description="Déconnexion utilisateur",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session.id
        )
        
        logger.info(f"Session déconnectée pour l'utilisateur {session.user_id}")
        
        return True
    
    def logout_all_sessions(self, user: User, ip_address: str,
                           user_agent: Optional[str] = None) -> bool:
        """
        Déconnecte toutes les sessions d'un utilisateur
        
        Args:
            user: Utilisateur concerné
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            
        Returns:
            True si la déconnexion a réussi
        """
        active_sessions = self.get_active_sessions(user)
        
        for session in active_sessions:
            session.is_active = False
            self._update_login_history(session, logout_time=datetime.utcnow())
        
        self.db.commit()
        
        # Journalise la déconnexion globale
        self._log_security_event(
            user_id=user.id,
            event_type="all_sessions_logout",
            severity="medium",
            description="Déconnexion de toutes les sessions",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Toutes les sessions déconnectées pour l'utilisateur {user.id}")
        
        return True
    
    def get_active_sessions(self, user: User) -> List[UserSession]:
        """
        Récupère toutes les sessions actives d'un utilisateur
        
        Args:
            user: Utilisateur concerné
            
        Returns:
            Liste des sessions actives
        """
        return self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).order_by(UserSession.last_activity.desc()).all()
    
    def get_session_history(self, user: User, limit: int = 50) -> List[LoginHistory]:
        """
        Récupère l'historique des connexions d'un utilisateur
        
        Args:
            user: Utilisateur concerné
            limit: Nombre maximum d'entrées à retourner
            
        Returns:
            Liste des historiques de connexion
        """
        return self.db.query(LoginHistory).filter(
            LoginHistory.user_id == user.id
        ).order_by(LoginHistory.login_at.desc()).limit(limit).all()
    
    def log_login_attempt(self, user: User, login_type: str, ip_address: str,
                         user_agent: Optional[str] = None, provider: Optional[str] = None,
                         success: bool = True, failure_reason: Optional[str] = None,
                         session: Optional[UserSession] = None) -> LoginHistory:
        """
        Journalise une tentative de connexion
        
        Args:
            user: Utilisateur concerné
            login_type: Type de connexion (password, oauth_google, etc.)
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            provider: Provider OAuth2 (si applicable)
            success: Si la connexion a réussi
            failure_reason: Raison de l'échec (si applicable)
            session: Session associée (si création de session)
            
        Returns:
            Entrée d'historique créée
        """
        # Détecte la localisation approximative (simplifié)
        location = self._detect_location(ip_address)
        
        login_history = LoginHistory(
            user_id=user.id,
            login_type=login_type,
            provider=provider,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            success=success,
            failure_reason=failure_reason,
            login_at=datetime.utcnow(),
            session_id=session.id if session else None
        )
        
        self.db.add(login_history)
        self.db.commit()
        self.db.refresh(login_history)
        
        # Journalise les échecs de connexion comme événements de sécurité
        if not success:
            self._log_security_event(
                user_id=user.id,
                event_type="login_failed",
                severity="medium",
                description=f"Tentative de connexion échouée: {failure_reason}",
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session.id if session else None
            )
        
        return login_history
    
    def cleanup_expired_sessions(self) -> int:
        """
        Nettoie les sessions expirées
        
        Returns:
            Nombre de sessions nettoyées
        """
        now = datetime.utcnow()
        
        # Récupère les sessions expirées
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at < now,
            UserSession.is_active == True
        ).all()
        
        count = len(expired_sessions)
        
        for session in expired_sessions:
            session.is_active = False
            self._update_login_history(session, logout_time=session.expires_at)
            
            # Journalise le nettoyage
            self._log_security_event(
                user_id=session.user_id,
                event_type="session_cleanup",
                severity="low",
                description="Session nettoyée automatiquement (expirée)",
                ip_address=session.ip_address,
                session_id=session.id
            )
        
        self.db.commit()
        
        if count > 0:
            logger.info(f"{count} sessions expirées nettoyées")
        
        return count
    
    def get_security_events(self, user: User, limit: int = 100) -> List[SecurityEvent]:
        """
        Récupère les événements de sécurité d'un utilisateur
        
        Args:
            user: Utilisateur concerné
            limit: Nombre maximum d'événements à retourner
            
        Returns:
            Liste des événements de sécurité
        """
        return self.db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user.id
        ).order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    
    def _generate_session_token(self) -> str:
        """Génère un token de session unique"""
        return secrets.token_urlsafe(64)
    
    def _generate_refresh_token(self) -> str:
        """Génère un token de rafraîchissement unique"""
        return secrets.token_urlsafe(64)
    
    def _parse_user_agent(self, user_agent: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """Parse le User-Agent pour extraire le navigateur et la plateforme"""
        if not user_agent:
            return None, None
        
        # Détection simplifiée
        user_agent_lower = user_agent.lower()
        
        # Navigateur
        if "chrome" in user_agent_lower:
            browser = "Chrome"
        elif "firefox" in user_agent_lower:
            browser = "Firefox"
        elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
            browser = "Safari"
        elif "edge" in user_agent_lower:
            browser = "Edge"
        else:
            browser = "Unknown"
        
        # Plateforme
        if "windows" in user_agent_lower:
            platform = "Windows"
        elif "mac" in user_agent_lower:
            platform = "macOS"
        elif "linux" in user_agent_lower:
            platform = "Linux"
        elif "android" in user_agent_lower:
            platform = "Android"
        elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
            platform = "iOS"
        else:
            platform = "Unknown"
        
        return browser, platform
    
    def _detect_location(self, ip_address: str) -> Optional[str]:
        """
        Détecte la localisation approximative à partir de l'IP
        Note: Dans une implémentation réelle, utiliser un service de géolocalisation
        """
        # Implémentation simplifiée - retourne None
        # Pour une implémentation réelle, utiliser:
        # - GeoIP2
        # - API de géolocalisation IP
        # - Service tiers
        return None
    
    def _update_login_history(self, session: UserSession, logout_time: datetime) -> None:
        """Met à jour l'historique de connexion avec l'heure de déconnexion"""
        # Trouve l'entrée d'historique la plus récente pour cette session
        login_history = self.db.query(LoginHistory).filter(
            LoginHistory.session_id == session.id,
            LoginHistory.logout_at.is_(None)
        ).order_by(LoginHistory.login_at.desc()).first()
        
        if login_history:
            login_history.logout_at = logout_time
            self.db.commit()
    
    def _log_security_event(self, user_id: int, event_type: str, severity: str,
                           description: str, ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None, session_id: Optional[int] = None) -> None:
        """Journalise un événement de sécurité"""
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(event)
        self.db.commit()


# Dépendance FastAPI
def get_session_service(db: Session) -> SessionService:
    """Dépendance pour obtenir le service de sessions"""
    return SessionService(db)