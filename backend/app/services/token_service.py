# backend/app/services/token_service.py
"""
Service pour la gestion des tokens JWT avec rafraîchissement automatique et rotation sécurisée
Gestion du cycle de vie des tokens d'accès et de rafraîchissement
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError

from app.models.session import UserSession
from app.models.user import User
from app.utils.logger import get_logger
from app.exceptions.session_exceptions import (
    TokenExpiredException,
    InvalidTokenException,
    TokenRevokedException
)

logger = get_logger(__name__)


class TokenService:
    """Service de gestion des tokens avec rotation sécurisée"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Configuration des tokens
        self.access_token_expire_minutes = 15  # 15 minutes
        self.refresh_token_expire_days = 7     # 7 jours
        self.max_refresh_tokens_per_user = 5   # Maximum de tokens de rafraîchissement actifs
        
        # Clés de chiffrement (doivent être dans les variables d'environnement en production)
        self.jwt_secret_key = "your-secret-key-change-in-production"
        self.jwt_algorithm = "HS256"
    
    def create_tokens(self, user: User, session: UserSession) -> Tuple[str, str]:
        """
        Crée une paire de tokens (access + refresh) avec rotation sécurisée
        
        Args:
            user: Utilisateur concerné
            session: Session associée
            
        Returns:
            Tuple (access_token, refresh_token)
        """
        # Token d'accès (courte durée)
        access_token = self._create_access_token(
            user_id=user.id,
            session_id=session.id,
            username=user.username
        )
        
        # Token de rafraîchissement (longue durée avec rotation)
        refresh_token = self._create_refresh_token(
            user_id=user.id,
            session_id=session.id
        )
        
        # Met à jour la session avec le nouveau refresh token
        session.refresh_token = refresh_token
        session.expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        self.db.commit()
        
        logger.info(f"Tokens créés pour l'utilisateur {user.id}, session {session.id}")
        
        return access_token, refresh_token
    
    def refresh_tokens(self, old_refresh_token: str, ip_address: str, 
                      user_agent: Optional[str] = None) -> Tuple[str, str, UserSession]:
        """
        Rafraîchit les tokens avec rotation sécurisée
        
        Args:
            old_refresh_token: Ancien token de rafraîchissement
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            
        Returns:
            Tuple (new_access_token, new_refresh_token, session)
        """
        # Valide l'ancien refresh token
        session = self._validate_refresh_token(old_refresh_token)
        
        if not session:
            raise InvalidTokenException("Refresh token invalide")
        
        # Vérifie que la session est toujours active
        if not session.is_active or session.is_expired():
            raise TokenExpiredException()
        
        # Vérifie la rotation (empêche la réutilisation du même refresh token)
        if session.refresh_token != old_refresh_token:
            raise TokenRevokedException("Refresh token déjà utilisé")
        
        # Crée de nouveaux tokens
        user = self.db.query(User).filter(User.id == session.user_id).first()
        if not user:
            raise InvalidTokenException("Utilisateur non trouvé")
        
        new_access_token, new_refresh_token = self.create_tokens(user, session)
        
        # Journalise le rafraîchissement
        logger.info(f"Tokens rafraîchis pour l'utilisateur {user.id}, session {session.id}")
        
        return new_access_token, new_refresh_token, session
    
    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """
        Valide un token d'accès et retourne les données décodées
        
        Args:
            token: Token JWT à valider
            
        Returns:
            Données décodées du token
            
        Raises:
            TokenExpiredException: Si le token est expiré
            InvalidTokenException: Si le token est invalide
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret_key, 
                algorithms=[self.jwt_algorithm]
            )
            
            # Vérifie l'expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
                raise TokenExpiredException()
            
            # Vérifie que la session existe et est active
            session_id = payload.get("session_id")
            if session_id:
                session = self.db.query(UserSession).filter(
                    UserSession.id == session_id,
                    UserSession.is_active == True
                ).first()
                
                if not session or session.is_expired():
                    raise TokenExpiredException()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except PyJWTError as e:
            raise InvalidTokenException(f"Token invalide: {str(e)}")
    
    def revoke_tokens(self, session_id: int) -> bool:
        """
        Révoque tous les tokens d'une session
        
        Args:
            session_id: ID de la session à révoquer
            
        Returns:
            True si la révocation a réussi
        """
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()
        
        if session:
            session.is_active = False
            session.refresh_token = None  # Invalide le refresh token
            self.db.commit()
            
            logger.info(f"Tokens révoqués pour la session {session_id}")
            return True
        
        return False
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Révoque tous les tokens d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nombre de sessions révoquées
        """
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        count = len(sessions)
        
        for session in sessions:
            session.is_active = False
            session.refresh_token = None
        
        self.db.commit()
        
        logger.info(f"Tous les tokens révoqués pour l'utilisateur {user_id} ({count} sessions)")
        
        return count
    
    def cleanup_expired_tokens(self) -> Dict[str, int]:
        """
        Nettoie les tokens expirés et révoqués
        
        Returns:
            Statistiques du nettoyage
        """
        now = datetime.utcnow()
        
        # Sessions expirées
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at < now,
            UserSession.is_active == True
        ).all()
        
        expired_count = len(expired_sessions)
        for session in expired_sessions:
            session.is_active = False
        
        # Refresh tokens expirés (mais sessions toujours actives)
        expired_refresh_tokens = self.db.query(UserSession).filter(
            UserSession.expires_at < now,
            UserSession.is_active == True
        ).all()
        
        refresh_expired_count = len(expired_refresh_tokens)
        for session in expired_refresh_tokens:
            session.refresh_token = None
        
        self.db.commit()
        
        stats = {
            "expired_sessions_cleaned": expired_count,
            "expired_refresh_tokens_cleaned": refresh_expired_count,
            "total_cleaned": expired_count + refresh_expired_count
        }
        
        if stats["total_cleaned"] > 0:
            logger.info(f"Nettoyage des tokens: {stats}")
        
        return stats
    
    def get_active_sessions_count(self, user_id: int) -> int:
        """
        Retourne le nombre de sessions actives pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nombre de sessions actives
        """
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).count()
    
    def _create_access_token(self, user_id: int, session_id: int, username: str) -> str:
        """Crée un token d'accès JWT"""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "username": username,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret_key, algorithm=self.jwt_algorithm)
    
    def _create_refresh_token(self, user_id: int, session_id: int) -> str:
        """Crée un token de rafraîchissement sécurisé"""
        # Utilise une méthode sécurisée pour générer le token
        refresh_token = secrets.token_urlsafe(64)
        
        # Ajoute un prefix pour identifier le type de token
        return f"rf_{user_id}_{session_id}_{refresh_token}"
    
    def _validate_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """Valide un token de rafraîchissement et retourne la session associée"""
        if not refresh_token.startswith("rf_"):
            return None
        
        try:
            # Extrait les informations du token
            parts = refresh_token.split('_')
            if len(parts) != 4:
                return None
            
            user_id = int(parts[1])
            session_id = int(parts[2])
            
            # Trouve la session
            session = self.db.query(UserSession).filter(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            ).first()
            
            return session
            
        except (ValueError, IndexError):
            return None
    
    def get_token_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Retourne les métriques des tokens pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Métriques des tokens
        """
        active_sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        now = datetime.utcnow()
        soon_expiring = 0
        
        for session in active_sessions:
            if session.expires_at < now + timedelta(hours=24):
                soon_expiring += 1
        
        return {
            "active_sessions": len(active_sessions),
            "soon_expiring_sessions": soon_expiring,
            "max_allowed_sessions": self.max_refresh_tokens_per_user,
            "access_token_duration_minutes": self.access_token_expire_minutes,
            "refresh_token_duration_days": self.refresh_token_expire_days
        }


# Dépendance FastAPI
def get_token_service(db: Session) -> TokenService:
    """Dépendance pour obtenir le service de tokens"""
    return TokenService(db)