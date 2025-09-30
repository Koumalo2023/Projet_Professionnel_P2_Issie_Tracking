#!/usr/bin/env python3
"""
Test des composants MFA sans dépendre du serveur en cours d'exécution
Teste les services, modèles et fonctionnalités de base du MFA
"""

import sys
import os
import json
import time
import base64
import hmac
import hashlib

# Ajouter le chemin du backend pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.mfa import MFASettings, MFALoginAttempt, MFARecoveryCode
from app.services.mfa_service import MFAService
from app.auth.auth_utils import get_password_hash

class MFAComponentTester:
    """Testeur des composants MFA"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.test_results = []
        self.test_user = None
        
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
            
    def setup_test_environment(self):
        """Configure l'environnement de test"""
        try:
            # Crée les tables si elles n'existent pas
            Base.metadata.create_all(bind=engine)
            
            # Crée un utilisateur de test
            self.test_user = User(
                username="test_mfa_component",
                email="test_mfa_component@example.com",
                hashed_password=get_password_hash("testpassword123"),
                is_active=True
            )
            self.db.add(self.test_user)
            self.db.commit()
            self.db.refresh(self.test_user)
            
            self.log_test("Configuration environnement", True, "Environnement de test configuré")
            return True
            
        except Exception as e:
            self.log_test("Configuration environnement", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_service_initialization(self):
        """Teste l'initialisation du service MFA"""
        try:
            mfa_service = MFAService(self.db)
            self.log_test("Initialisation service MFA", True, "Service MFA initialisé avec succès")
            return mfa_service
        except Exception as e:
            self.log_test("Initialisation service MFA", False, f"Erreur: {str(e)}")
            return None

    def test_secret_key_generation(self, mfa_service):
        """Teste la génération de clé secrète"""
        try:
            secret_key = mfa_service.generate_secret_key()
            is_valid = len(secret_key) >= 16 and all(c.isalnum() for c in secret_key)
            
            self.log_test("Génération clé secrète", is_valid, 
                         f"Clé secrète générée: {secret_key[:10]}...", {
                             "length": len(secret_key),
                             "format_valid": is_valid
                         })
            return secret_key if is_valid else None
        except Exception as e:
            self.log_test("Génération clé secrète", False, f"Erreur: {str(e)}")
            return None

    def test_backup_codes_generation(self, mfa_service):
        """Teste la génération de codes de secours"""
        try:
            backup_codes = mfa_service.generate_backup_codes()
            is_valid = len(backup_codes) == 10 and all(len(code) == 8 for code in backup_codes)
            
            self.log_test("Génération codes secours", is_valid, 
                         f"{len(backup_codes)} codes générés", {
                             "codes_count": len(backup_codes),
                             "code_lengths": [len(code) for code in backup_codes]
                         })
            return backup_codes if is_valid else None
        except Exception as e:
            self.log_test("Génération codes secours", False, f"Erreur: {str(e)}")
            return None

    def test_backup_code_hashing(self, mfa_service):
        """Teste le hachage des codes de secours"""
        try:
            test_code = "TEST1234"
            hashed_code = mfa_service.hash_backup_code(test_code)
            is_valid = len(hashed_code) == 64 and hashed_code.isalnum()
            
            self.log_test("Hachage codes secours", is_valid, 
                         "Code hashé avec succès", {
                             "original_length": len(test_code),
                             "hashed_length": len(hashed_code),
                             "hash_format": "SHA-256" if is_valid else "Invalide"
                         })
            return hashed_code if is_valid else None
        except Exception as e:
            self.log_test("Hachage codes secours", False, f"Erreur: {str(e)}")
            return None

    def test_totp_code_generation(self, mfa_service, secret_key):
        """Teste la génération de codes TOTP"""
        try:
            # Test avec un timestamp spécifique pour la reproductibilité
            test_timestamp = int(time.time() // 30)
            generated_code = mfa_service._generate_totp_code(secret_key, test_timestamp)
            
            is_valid = len(generated_code) == 6 and generated_code.isdigit()
            
            self.log_test("Génération code TOTP", is_valid, 
                         f"Code généré: {generated_code}", {
                             "code_length": len(generated_code),
                             "is_numeric": generated_code.isdigit(),
                             "timestamp": test_timestamp
                         })
            return generated_code if is_valid else None
        except Exception as e:
            self.log_test("Génération code TOTP", False, f"Erreur: {str(e)}")
            return None

    def test_totp_code_verification(self, mfa_service, secret_key, valid_code):
        """Teste la vérification de codes TOTP"""
        try:
            # Test avec un code valide
            is_valid = mfa_service.verify_totp_code(secret_key, valid_code)
            
            # Test avec un code invalide
            is_invalid_rejected = not mfa_service.verify_totp_code(secret_key, "000000")
            
            self.log_test("Vérification code TOTP", is_valid and is_invalid_rejected, 
                         "Vérification TOTP fonctionnelle", {
                             "valid_code_accepted": is_valid,
                             "invalid_code_rejected": is_invalid_rejected
                         })
            return is_valid and is_invalid_rejected
        except Exception as e:
            self.log_test("Vérification code TOTP", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_setup_workflow(self, mfa_service):
        """Teste le workflow complet de configuration MFA"""
        try:
            # Étape 1: Configuration MFA
            setup_data = mfa_service.setup_mfa(self.test_user, "totp")
            
            # Vérifie les données de setup
            setup_success = (
                "secret_key" in setup_data and
                "backup_codes" in setup_data and
                "method" in setup_data and
                setup_data["method"] == "totp"
            )
            
            if not setup_success:
                self.log_test("Workflow configuration MFA", False, "Échec de l'étape de configuration")
                return False
            
            # Étape 2: Vérification avec un code valide
            valid_code = mfa_service._generate_totp_code(setup_data["secret_key"], int(time.time() // 30))
            verification_success = mfa_service.verify_mfa_setup(self.test_user, valid_code)
            
            # Étape 3: Vérification du statut
            status_data = mfa_service.get_mfa_status(self.test_user)
            
            workflow_success = (
                setup_success and 
                verification_success and 
                status_data["is_enabled"] and 
                status_data["is_setup"]
            )
            
            self.log_test("Workflow configuration MFA", workflow_success, 
                         "Workflow MFA complété", {
                             "setup_success": setup_success,
                             "verification_success": verification_success,
                             "mfa_enabled": status_data["is_enabled"],
                             "mfa_setup": status_data["is_setup"]
                         })
            return workflow_success
            
        except Exception as e:
            self.log_test("Workflow configuration MFA", False, f"Erreur: {str(e)}")
            return False

    def test_recovery_codes_workflow(self, mfa_service):
        """Teste le workflow des codes de récupération"""
        try:
            # Génère de nouveaux codes de récupération
            recovery_codes = mfa_service.generate_new_recovery_codes(self.test_user)
            
            # Vérifie que les codes sont générés
            generation_success = len(recovery_codes) == 10
            
            if not generation_success:
                self.log_test("Workflow codes récupération", False, "Échec de la génération des codes")
                return False
            
            # Teste la vérification d'un code de récupération
            test_code = recovery_codes[0]
            code_hash = mfa_service.hash_backup_code(test_code)
            
            # Simule l'utilisation d'un code de récupération
            recovery_code = MFARecoveryCode(
                user_id=self.test_user.id,
                code_hash=code_hash,
                is_used=False
            )
            self.db.add(recovery_code)
            self.db.commit()
            
            # Vérifie le code
            verification_success = mfa_service._verify_recovery_code(self.test_user, test_code)
            
            # Vérifie que le code est marqué comme utilisé
            used_code = self.db.query(MFARecoveryCode).filter(
                MFARecoveryCode.code_hash == code_hash
            ).first()
            
            workflow_success = (
                generation_success and
                verification_success and
                used_code.is_used
            )
            
            self.log_test("Workflow codes récupération", workflow_success, 
                         "Workflow codes récupération complété", {
                             "codes_generated": len(recovery_codes),
                             "code_verified": verification_success,
                             "code_marked_used": used_code.is_used if used_code else False
                         })
            return workflow_success
            
        except Exception as e:
            self.log_test("Workflow codes récupération", False, f"Erreur: {str(e)}")
            return False

    def test_mfa_disable_workflow(self, mfa_service):
        """Teste la désactivation MFA"""
        try:
            # Désactive le MFA
            mfa_service.disable_mfa(self.test_user)
            
            # Vérifie le statut après désactivation
            status_data = mfa_service.get_mfa_status(self.test_user)
            
            disable_success = not status_data["is_enabled"] and not status_data["is_setup"]
            
            self.log_test("Désactivation MFA", disable_success, 
                         "MFA désactivé avec succès", {
                             "mfa_enabled_after_disable": status_data["is_enabled"],
                             "mfa_setup_after_disable": status_data["is_setup"]
                         })
            return disable_success
            
        except Exception as e:
            self.log_test("Désactivation MFA", False, f"Erreur: {str(e)}")
            return False

    def cleanup_test_environment(self):
        """Nettoie l'environnement de test"""
        try:
            if self.test_user:
                # Supprime toutes les données MFA associées
                self.db.query(MFALoginAttempt).filter(MFALoginAttempt.user_id == self.test_user.id).delete()
                self.db.query(MFARecoveryCode).filter(MFARecoveryCode.user_id == self.test_user.id).delete()
                self.db.query(MFASettings).filter(MFASettings.user_id == self.test_user.id).delete()
                self.db.query(User).filter(User.id == self.test_user.id).delete()
                self.db.commit()
            
            self.db.close()
            self.log_test("Nettoyage environnement", True, "Environnement de test nettoyé")
        except Exception as e:
            self.log_test("Nettoyage environnement", False, f"Erreur: {str(e)}")

    def run_all_tests(self):
        """Exécute tous les tests des composants MFA"""
        print("🔧 DÉMARRAGE DES TESTS DES COMPOSANTS MFA")
        print("=" * 60)
        
        # Configuration initiale
        if not self.setup_test_environment():
            return False
        
        try:
            # Initialisation du service
            mfa_service = self.test_mfa_service_initialization()
            if not mfa_service:
                return False
            
            # Tests de base
            secret_key = self.test_secret_key_generation(mfa_service)
            backup_codes = self.test_backup_codes_generation(mfa_service)
            hashed_code = self.test_backup_code_hashing(mfa_service)
            
            if secret_key:
                generated_code = self.test_totp_code_generation(mfa_service, secret_key)
                if generated_code:
                    self.test_totp_code_verification(mfa_service, secret_key, generated_code)
            
            # Tests de workflow
            self.test_mfa_setup_workflow(mfa_service)
            self.test_recovery_codes_workflow(mfa_service)
            self.test_mfa_disable_workflow(mfa_service)
            
            return self.generate_report()
            
        finally:
            # Nettoyage
            self.cleanup_test_environment()

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
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test_type": "Composants MFA (sans serveur)"
            },
            "test_results": self.test_results
        }
        
        # Sauvegarde le rapport dans un fichier
        report_filename = f"mfa_components_test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Affiche le résumé
        print("\n" + "=" * 60)
        print("📊 RAPPORT DE TEST DES COMPOSANTS MFA")
        print("=" * 60)
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {successful_tests}")
        print(f"Tests échoués: {total_tests - successful_tests}")
        print(f"Taux de succès: {success_rate:.2f}%")
        print(f"Rapport sauvegardé: {report_filename}")
        
        return success_rate >= 80  # Seuil de 80% pour considérer le test réussi

if __name__ == "__main__":
    tester = MFAComponentTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)