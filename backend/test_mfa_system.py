#!/usr/bin/env python3
"""
Script de test complet pour le système MFA
Teste toutes les fonctionnalités de l'authentification multi-facteurs
"""

import sys
import os
import requests
import json
import time
import base64
import hmac
import hashlib
import struct

# Ajouter le chemin du backend pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.models.user import User
from app.models.mfa import MFASettings
from app.services.mfa_service import MFAService

# Configuration de base
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "test_mfa_user"
TEST_PASSWORD = "testpassword123"
TEST_EMAIL = "test_mfa@example.com"

class MFATestRunner:
    """Runner pour les tests du système MFA"""
    
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Enregistre un résultat de test"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✓ SUCCÈS" if success else "✗ ÉCHEC"
        print(f"{status} - {test_name}: {message}")
        if details:
            print(f"   Détails: {details}")
            
    def generate_totp_code(self, secret_key):
        """Génère un code TOTP valide pour les tests"""
        # Implémentation simplifiée de TOTP
        import time
        current_time = int(time.time() // 30)
        
        # Ajoute le padding si nécessaire
        secret_key = secret_key + '=' * ((8 - len(secret_key) % 8) % 8)
        
        try:
            # Décode la clé secrète
            key = base64.b32decode(secret_key, casefold=True)
            
            # Convertit le timestamp en bytes (8 bytes, big-endian)
            msg = current_time.to_bytes(8, byteorder='big')
            
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
            return "123456"  # Code de fallback pour les tests

    def setup_test_user(self):
        """Crée un utilisateur de test"""
        try:
            db = SessionLocal()
            
            # Vérifie si l'utilisateur existe déjà
            existing_user = db.query(User).filter(User.username == TEST_USERNAME).first()
            if existing_user:
                # Supprime les données MFA existantes
                db.query(MFASettings).filter(MFASettings.user_id == existing_user.id).delete()
                db.delete(existing_user)
                db.commit()
            
            # Crée un nouvel utilisateur
            from app.auth.auth_utils import get_password_hash
            user = User(
                username=TEST_USERNAME,
                email=TEST_EMAIL,
                hashed_password=get_password_hash(TEST_PASSWORD),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            self.user_id = user.id
            
            self.log_test("Création utilisateur test", True, f"Utilisateur créé avec ID: {user.id}")
            return True
            
        except Exception as e:
            self.log_test("Création utilisateur test", False, f"Erreur: {str(e)}")
            return False
        finally:
            db.close()

    def authenticate_user(self):
        """Authentifie l'utilisateur de test"""
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log_test("Authentification", True, "Utilisateur authentifié avec succès")
                return True
            else:
                self.log_test("Authentification", False, f"Échec de l'authentification: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentification", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_setup(self):
        """Teste la configuration MFA"""
        try:
            response = self.session.post(f"{BASE_URL}/api/mfa/setup", json={
                "method": "totp"
            })
            
            if response.status_code == 200:
                data = response.json()
                secret_key = data.get("secret_key")
                backup_codes = data.get("backup_codes")
                qr_code_url = data.get("qr_code_url")
                
                self.log_test("Configuration MFA", True, "Configuration MFA réussie", {
                    "secret_key": secret_key[:10] + "...",
                    "backup_codes_count": len(backup_codes),
                    "qr_code_url": qr_code_url is not None
                })
                
                # Sauvegarde la clé secrète pour les tests suivants
                self.secret_key = secret_key
                self.backup_codes = backup_codes
                return True
            else:
                self.log_test("Configuration MFA", False, f"Échec de la configuration: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Configuration MFA", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_verification(self):
        """Teste la vérification MFA"""
        try:
            # Génère un code TOTP valide
            valid_code = self.generate_totp_code(self.secret_key)
            
            response = self.session.post(f"{BASE_URL}/api/mfa/verify", json={
                "code": valid_code
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Vérification MFA", True, "Vérification MFA réussie")
                    return True
                else:
                    self.log_test("Vérification MFA", False, "Code MFA invalide")
                    return False
            else:
                self.log_test("Vérification MFA", False, f"Échec de la vérification: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Vérification MFA", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_status(self):
        """Teste la récupération du statut MFA"""
        try:
            response = self.session.get(f"{BASE_URL}/api/mfa/status")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Statut MFA", True, "Statut MFA récupéré", data)
                return True
            else:
                self.log_test("Statut MFA", False, f"Échec de la récupération: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Statut MFA", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_enable(self):
        """Teste l'activation MFA"""
        try:
            # Génère un code TOTP valide
            valid_code = self.generate_totp_code(self.secret_key)
            
            response = self.session.post(f"{BASE_URL}/api/mfa/enable", json={
                "code": valid_code
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Activation MFA", True, "MFA activé avec succès")
                    return True
                else:
                    self.log_test("Activation MFA", False, "Échec de l'activation")
                    return False
            else:
                self.log_test("Activation MFA", False, f"Échec de l'activation: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Activation MFA", False, f"Erreur: {str(e)}")
            return False

    def test_recovery_codes_generation(self):
        """Teste la génération de codes de récupération"""
        try:
            response = self.session.post(f"{BASE_URL}/api/mfa/recovery-codes/generate")
            
            if response.status_code == 200:
                data = response.json()
                recovery_codes = data.get("recovery_codes")
                self.log_test("Génération codes récupération", True, 
                             f"{len(recovery_codes)} codes générés", {
                                 "codes_count": len(recovery_codes)
                             })
                self.recovery_codes = recovery_codes
                return True
            else:
                self.log_test("Génération codes récupération", False, 
                             f"Échec de la génération: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Génération codes récupération", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_settings(self):
        """Teste la récupération des paramètres MFA"""
        try:
            response = self.session.get(f"{BASE_URL}/api/mfa/settings")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Paramètres MFA", True, "Paramètres MFA récupérés", {
                    "is_enabled": data.get("is_enabled"),
                    "method": data.get("method")
                })
                return True
            else:
                self.log_test("Paramètres MFA", False, f"Échec de la récupération: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Paramètres MFA", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_attempts(self):
        """Teste la récupération des tentatives MFA"""
        try:
            response = self.session.get(f"{BASE_URL}/api/mfa/attempts")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Tentatives MFA", True, f"{len(data)} tentatives récupérées", {
                    "attempts_count": len(data)
                })
                return True
            else:
                self.log_test("Tentatives MFA", False, f"Échec de la récupération: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Tentatives MFA", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_disable(self):
        """Teste la désactivation MFA"""
        try:
            response = self.session.post(f"{BASE_URL}/api/mfa/disable", json={
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Désactivation MFA", True, "MFA désactivé avec succès")
                    return True
                else:
                    self.log_test("Désactivation MFA", False, "Échec de la désactivation")
                    return False
            else:
                self.log_test("Désactivation MFA", False, f"Échec de la désactivation: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Désactivation MFA", False, f"Erreur: {str(e)}")
            return False

    def run_all_tests(self):
        """Exécute tous les tests MFA"""
        print("🚀 DÉMARRAGE DES TESTS MFA")
        print("=" * 50)
        
        # Configuration initiale
        if not self.setup_test_user():
            return False
            
        if not self.authenticate_user():
            return False
        
        # Tests MFA
        tests = [
            self.test_mfa_setup,
            self.test_mfa_verification,
            self.test_mfa_status,
            self.test_mfa_enable,
            self.test_recovery_codes_generation,
            self.test_mfa_settings,
            self.test_mfa_attempts,
            self.test_mfa_disable
        ]
        
        for test in tests:
            test()
            
        # Nettoyage
        self.cleanup_test_user()
        
        return self.generate_report()

    def cleanup_test_user(self):
        """Nettoie l'utilisateur de test"""
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.username == TEST_USERNAME).first()
            if user:
                db.query(MFASettings).filter(MFASettings.user_id == user.id).delete()
                db.delete(user)
                db.commit()
                self.log_test("Nettoyage", True, "Utilisateur de test supprimé")
            db.close()
        except Exception as e:
            self.log_test("Nettoyage", False, f"Erreur lors du nettoyage: {str(e)}")

    def generate_report(self):
        """Génère un rapport de test complet"""
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": round(success_rate, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "test_results": self.test_results
        }
        
        # Sauvegarde le rapport dans un fichier
        report_filename = f"mfa_test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Affiche le résumé
        print("\n" + "=" * 50)
        print("📊 RAPPORT DE TEST MFA")
        print("=" * 50)
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {successful_tests}")
        print(f"Tests échoués: {total_tests - successful_tests}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Rapport sauvegardé: {report_filename}")
        
        return success_rate == 100

if __name__ == "__main__":
    # Vérifie que le serveur est en cours d'exécution
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Le serveur FastAPI ne semble pas être en cours d'exécution")
            print("Veuillez démarrer le serveur avec: uvicorn app.main:app --reload")
            sys.exit(1)
    except requests.ConnectionError:
        print("❌ Impossible de se connecter au serveur FastAPI")
        print("Veuillez démarrer le serveur avec: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Exécute les tests
    test_runner = MFATestRunner()
    success = test_runner.run_all_tests()
    
    sys.exit(0 if success else 1)