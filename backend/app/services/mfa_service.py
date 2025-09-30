# app/services/mfa_service.py
"""
Service pour l'authentification multi-facteurs (MFA)
Gère la génération, validation et gestion des codes MFA
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.mfa import MFASettings, MFALoginAttempt, MFARecoveryCode
from app.models.user import User
from app.exceptions.mfa_exceptions import (
    MFAAlreadyEnabledException,
    MFANotEnabledException,
    MFAInvalidCodeException,
    MFAInvalidRecoveryCodeException,
    MFARateLimitException,
    MFANotConfiguredException
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MFAService:
    """Service de gestion de l'authentification multi-facteurs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_secret_key(self) -> str:
        """Génère une clé secrète pour TOTP"""
        # Génère 20 bytes aléatoires (recommandé par RFC 6238)
        secret_bytes = secrets.token_bytes(20)
        # Encode en base32 (sans padding pour compatibilité)
        secret_key = base64.b32encode(secret_bytes).decode('utf-8').rstrip('=')
        return secret_key
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Génère des codes de secours"""
        backup_codes = []
        for _ in range(count):
            # Génère un code de 8 caractères alphanumériques
            code = secrets.token_urlsafe(6).upper()[:8]
            backup_codes.append(code)
        return backup_codes
    
    def hash_backup_code(self, code: str) -> str:
        """Hash un code de secours pour le stockage sécurisé"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_totp_code(self, secret_key: str, code: str, window: int = 1) -> bool:
        """
        Vérifie un code TOTP
        
        Args:
            secret_key: Clé secrète TOTP
            code: Code à vérifier (6 chiffres)
            window: Fenêtre de temps (en pas de 30 secondes)
        
        Returns:
            bool: True si le code est valide
        """
        try:
            # Vérifie que le code est bien 6 chiffres
            if len(code) != 6 or not code.isdigit():
                return False
            
            # Temps actuel en pas de 30 secondes
            current_time = int(time.time() // 30)
            
            # Vérifie dans la fenêtre de temps
            for i in range(-window, window + 1):
                expected_code = self._generate_totp_code(secret_key, current_time + i)
                if hmac.compare_digest(code, expected_code):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification TOTP: {e}")
            return False
    
    def _generate_totp_code(self, secret_key: str, timestamp: int) -> str:
        """Génère un code TOTP pour un timestamp donné"""
        # Ajoute le padding si nécessaire
        secret_key = secret_key + '=' * ((8 - len(secret_key) % 8) % 8)
        
        try:
            # Décode la clé secrète
            key = base64.b32decode(secret_key, casefold=True)
            
            # Convertit le timestamp en bytes (8 bytes, big-endian)
            msg = timestamp.to_bytes(8, byteorder='big')
            
            # Calcule le HMAC-SHA1
            hmac_digest = hmac.new(key, msg, hashlib.sha1).digest()
            
            # Extrait le code dynamique (RFC 4226)
            offset = hmac_digest[-1] & 0xf
            code = ((hmac_digest[offset] & 0x7f) << 24 |
                   (hmac_digest[offset + 1] & 0xff) << 16 |
                   (hmac_digest[offset + 2] & 0xff) << 8 |
                   (hmac_digest[offset + 3] & 0xff))
            
            # Formate en 6 chiffres
            code = code % 1000000
            return f"{code:06d}"
        except Exception as e:
            logger.error(f"Erreur lors de la génération TOTP: {e}")
            return "000000"
    
    def setup_mfa(self, user: User, method: str = "totp") -> Dict[str, Any]:
        """
        Configure le MFA pour un utilisateur
        
        Returns:
            Dict avec la clé secrète et les codes de secours
        """
        # Vérifie si le MFA est déjà activé
        existing_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if existing_settings and existing_settings.is_enabled:
            raise MFAAlreadyEnabledException()
        
        # Génère la clé secrète
        secret_key = self.generate_secret_key()
        
        # Génère les codes de secours
        backup_codes = self.generate_backup_codes()
        backup_codes_hashed = [self.hash_backup_code(code) for code in backup_codes]
        
        # Crée ou met à jour les paramètres MFA
        if existing_settings:
            existing_settings.secret_key = secret_key
            existing_settings.method = method
            existing_settings.backup_codes = json.dumps(backup_codes_hashed)
        else:
            mfa_settings = MFASettings(
                user_id=user.id,
                secret_key=secret_key,
                method=method,
                backup_codes=json.dumps(backup_codes_hashed)
            )
            self.db.add(mfa_settings)
        
        self.db.commit()
        
        # Log l'action
        self._log_mfa_attempt(
            user.id, "setup", "127.0.0.1", "MFA setup initiated", True
        )
        
        return {
            "secret_key": secret_key,
            "backup_codes": backup_codes,  # Retourné uniquement lors du setup
            "method": method
        }
    
    def verify_mfa_setup(self, user: User, code: str) -> bool:
        """
        Vérifie le code MFA lors de la configuration initiale
        """
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings or not mfa_settings.secret_key:
            raise MFANotEnabledException()
        
        if self.verify_totp_code(mfa_settings.secret_key, code):
            # Active le MFA
            mfa_settings.is_enabled = True
            self.db.commit()
            
            self._log_mfa_attempt(
                user.id, "setup", "127.0.0.1", "MFA setup completed", True
            )
            return True
        else:
            self._log_mfa_attempt(
                user.id, "setup", "127.0.0.1", "Invalid setup code", False
            )
            raise MFAInvalidCodeException()
    
    def enable_mfa(self, user: User) -> None:
        """Active le MFA pour un utilisateur"""
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings:
            raise MFANotEnabledException("MFA non configuré")
        
        mfa_settings.is_enabled = True
        self.db.commit()
        
        self._log_mfa_attempt(
            user.id, "enable", "127.0.0.1", "MFA enabled", True
        )
    
    def disable_mfa(self, user: User) -> None:
        """Désactive le MFA pour un utilisateur"""
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings:
            raise MFANotEnabledException("MFA non configuré")
        
        mfa_settings.is_enabled = False
        mfa_settings.secret_key = None
        mfa_settings.backup_codes = None
        
        # Supprime les codes de récupération
        self.db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user.id
        ).delete()
        
        self.db.commit()
        
        self._log_mfa_attempt(
            user.id, "disable", "127.0.0.1", "MFA disabled", True
        )
    
    def verify_login_code(self, user: User, code: str, ip_address: str) -> bool:
        """
        Vérifie un code MFA lors de la connexion
        """
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id,
            MFASettings.is_enabled == True
        ).first()
        
        if not mfa_settings:
            raise MFANotEnabledException()
        
        # Vérifie d'abord si c'est un code de récupération
        if self._verify_recovery_code(user, code):
            self._log_mfa_attempt(
                user.id, "recovery", ip_address, "Recovery code used", True
            )
            return True
        
        # Vérifie le code TOTP
        if self.verify_totp_code(mfa_settings.secret_key, code):
            self._log_mfa_attempt(
                user.id, "login", ip_address, "MFA login successful", True
            )
            return True
        else:
            self._log_mfa_attempt(
                user.id, "login", ip_address, "Invalid MFA code", False
            )
            raise MFAInvalidCodeException()
    
    def _verify_recovery_code(self, user: User, code: str) -> bool:
        """Vérifie un code de récupération"""
        code_hash = self.hash_backup_code(code)
        
        recovery_code = self.db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user.id,
            MFARecoveryCode.code_hash == code_hash,
            MFARecoveryCode.is_used == False
        ).first()
        
        if recovery_code:
            recovery_code.is_used = True
            recovery_code.used_at = time.time()
            self.db.commit()
            return True
        
        return False
    
    def get_mfa_status(self, user: User) -> Dict[str, Any]:
        """Retourne le statut MFA d'un utilisateur"""
        mfa_settings = self.db.query(MFASettings).filter(
            MFASettings.user_id == user.id
        ).first()
        
        if not mfa_settings:
            return {
                "is_enabled": False,
                "is_setup": False,
                "method": None
            }
        
        return {
            "is_enabled": mfa_settings.is_enabled,
            "is_setup": bool(mfa_settings.secret_key),
            "method": mfa_settings.method
        }
    
    def generate_new_recovery_codes(self, user: User) -> List[str]:
        """Génère de nouveaux codes de récupération"""
        # Supprime les anciens codes
        self.db.query(MFARecoveryCode).filter(
            MFARecoveryCode.user_id == user.id
        ).delete()
        
        # Génère de nouveaux codes
        new_codes = self.generate_backup_codes()
        
        # Stocke les codes hashés
        for code in new_codes:
            recovery_code = MFARecoveryCode(
                user_id=user.id,
                code_hash=self.hash_backup_code(code)
            )
            self.db.add(recovery_code)
        
        self.db.commit()
        
        self._log_mfa_attempt(
            user.id, "recovery_generate", "127.0.0.1", "New recovery codes generated", True
        )
        
        return new_codes
    
    def _log_mfa_attempt(self, user_id: int, attempt_type: str, ip_address: str, 
                        reason: str, success: bool) -> None:
        """Log une tentative MFA"""
        attempt = MFALoginAttempt(
            user_id=user_id,
            attempt_type=attempt_type,
            ip_address=ip_address,
            success=success,
            failure_reason=reason if not success else None
        )
        self.db.add(attempt)
        self.db.commit()


# Dépendance FastAPI
def get_mfa_service(db: Session) -> MFAService:
    """Dépendance pour obtenir le service MFA"""
    return MFAService(db)