# backend/tests/test_mfa_controller.py
"""
Tests pour le contrôleur MFA (Multi-Factor Authentication)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User
from app.models.mfa import MFASettings, MFALoginAttempt, MFARecoveryCode
from app.auth.auth_utils import create_access_token

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables
Base.metadata.create_all(bind=engine)

# Dépendance de base de données de test
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestMFAController:
    """Tests pour le contrôleur MFA"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.db = TestingSessionLocal()
        
        # Nettoyer les données de test
        self.db.query(MFALoginAttempt).delete()
        self.db.query(MFARecoveryCode).delete()
        self.db.query(MFASettings).delete()
        self.db.query(User).delete()
        self.db.commit()
        
        # Créer un utilisateur de test
        self.test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="fakehashedpassword",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=True
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)
        
        # Créer un token d'accès pour l'utilisateur
        self.access_token = create_access_token(data={"sub": str(self.test_user.id)})
        
        # Headers d'authentification
        self.auth_headers = {"Authorization": f"Bearer {self.access_token}"}
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.db.close()
    
    def test_setup_mfa_success(self):
        """Test la configuration MFA réussie"""
        response = client.post(
            "/api/mfa/setup",
            json={"method": "totp"},
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "secret_key" in data
        assert "backup_codes" in data
        assert "qr_code_url" in data
        assert len(data["backup_codes"]) == 10
        assert data["method"] == "totp"
    
    def test_setup_mfa_already_enabled(self):
        """Test la configuration MFA quand déjà activé"""
        # Configurer d'abord le MFA
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY"
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        # Tenter de reconfigurer
        response = client.post(
            "/api/mfa/setup",
            json={"method": "totp"},
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_get_mfa_status_not_setup(self):
        """Test la récupération du statut MFA quand non configuré"""
        response = client.get(
            "/api/mfa/status",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_enabled"] == False
        assert data["is_setup"] == False
        assert data["setup_required"] == True
    
    def test_get_mfa_status_setup_but_not_enabled(self):
        """Test la récupération du statut MFA quand configuré mais non activé"""
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=False,
            method="totp",
            secret_key="TESTSECRETKEY"
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        response = client.get(
            "/api/mfa/status",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_enabled"] == False
        assert data["is_setup"] == True
        assert data["setup_required"] == False
    
    def test_get_mfa_status_enabled(self):
        """Test la récupération du statut MFA quand activé"""
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY"
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        response = client.get(
            "/api/mfa/status",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_enabled"] == True
        assert data["is_setup"] == True
        assert data["setup_required"] == False
    
    def test_generate_recovery_codes_success(self):
        """Test la génération de codes de récupération"""
        # Configurer d'abord le MFA
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY"
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        response = client.post(
            "/api/mfa/recovery-codes/generate",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recovery_codes" in data
        assert len(data["recovery_codes"]) == 10
    
    def test_generate_recovery_codes_not_enabled(self):
        """Test la génération de codes de récupération sans MFA activé"""
        response = client.post(
            "/api/mfa/recovery-codes/generate",
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_get_mfa_settings_success(self):
        """Test la récupération des paramètres MFA"""
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY"
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        response = client.get(
            "/api/mfa/settings",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == self.test_user.id
        assert data["is_enabled"] == True
        assert data["method"] == "totp"
    
    def test_get_mfa_settings_not_found(self):
        """Test la récupération des paramètres MFA quand non trouvés"""
        response = client.get(
            "/api/mfa/settings",
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_mfa_attempts_success(self):
        """Test la récupération des tentatives MFA"""
        # Créer quelques tentatives de test
        for i in range(3):
            attempt = MFALoginAttempt(
                user_id=self.test_user.id,
                attempt_type="login",
                ip_address=f"192.168.1.{i}",
                success=(i % 2 == 0),
                failure_reason="Invalid code" if i % 2 != 0 else None
            )
            self.db.add(attempt)
        self.db.commit()
        
        response = client.get(
            "/api/mfa/attempts?limit=5",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(attempt["user_id"] == self.test_user.id for attempt in data)
    
    def test_get_mfa_stats_success(self):
        """Test la récupération des statistiques MFA"""
        # Créer des données de test
        user2 = User(
            username="testuser2",
            email="test2@example.com",
            hashed_password="fakehashedpassword2",
            age=30,
            can_be_contacted=True,
            can_data_be_shared=True
        )
        self.db.add(user2)
        
        # MFA activé pour le premier utilisateur
        mfa_settings1 = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY1"
        )
        self.db.add(mfa_settings1)
        
        # MFA configuré mais non activé pour le deuxième utilisateur
        mfa_settings2 = MFASettings(
            user_id=user2.id,
            is_enabled=False,
            method="totp",
            secret_key="TESTSECRETKEY2"
        )
        self.db.add(mfa_settings2)
        
        self.db.commit()
        
        response = client.get(
            "/api/mfa/stats",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 2
        assert data["mfa_enabled_users"] == 1
        assert data["mfa_setup_users"] == 2
        assert data["mfa_usage_rate"] == 50.0  # 1 sur 2 utilisateurs
    
    def test_verify_mfa_login_not_enabled(self):
        """Test la vérification MFA lors de la connexion sans MFA activé"""
        response = client.post(
            "/api/mfa/verify-login",
            json={"code": "123456"},
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_verify_recovery_code_not_enabled(self):
        """Test la vérification d'un code de récupération sans MFA activé"""
        response = client.post(
            "/api/mfa/recovery/verify",
            json={"code": "ABCD1234"},
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_get_recovery_codes_not_found(self):
        """Test la récupération des codes de récupération quand non trouvés"""
        response = client.get(
            "/api/mfa/recovery-codes",
            headers=self.auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_recovery_codes_success(self):
        """Test la récupération des codes de récupération"""
        # Configurer MFA avec codes de secours
        backup_codes = ["CODE1", "CODE2", "CODE3"]
        import json
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY",
            backup_codes=json.dumps(backup_codes)
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        response = client.get(
            "/api/mfa/recovery-codes",
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recovery_codes" in data
        # Les codes réels ne sont pas renvoyés pour des raisons de sécurité
        assert data["recovery_codes"] == ["*** Masqué pour la sécurité ***"] * 3
    
    def test_disable_mfa_success(self):
        """Test la désactivation du MFA"""
        # Configurer d'abord le MFA
        mfa_settings = MFASettings(
            user_id=self.test_user.id,
            is_enabled=True,
            method="totp",
            secret_key="TESTSECRETKEY"
        )
        self.db.add(mfa_settings)
        self.db.commit()
        
        response = client.post(
            "/api/mfa/disable",
            json={"password": "testpassword"},  # Le mot de passe n'est pas vérifié dans le test
            headers=self.auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "désactivé" in data["message"].lower()
    
    def test_disable_mfa_not_enabled(self):
        """Test la désactivation du MFA quand non activé"""
        response = client.post(
            "/api/mfa/disable",
            json={"password": "testpassword"},
            headers=self.auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestMFAServiceIntegration:
    """Tests d'intégration pour le service MFA"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.db = TestingSessionLocal()
        
        # Nettoyer les données de test
        self.db.query(MFALoginAttempt).delete()
        self.db.query(MFARecoveryCode).delete()
        self.db.query(MFASettings).delete()
        self.db.query(User).delete()
        self.db.commit()
        
        # Créer un utilisateur de test
        self.test_user = User(
            username="integrationuser",
            email="integration@example.com",
            hashed_password="fakehashedpassword",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=True
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)
        
        # Créer un token d'accès pour l'utilisateur
        self.access_token = create_access_token(data={"sub": str(self.test_user.id)})
        self.auth_headers = {"Authorization": f"Bearer {self.access_token}"}
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        self.db.close()
    
    def test_complete_mfa_workflow(self):
        """Test le workflow complet de configuration et utilisation MFA"""
        # Étape 1: Configuration MFA
        setup_response = client.post(
            "/api/mfa/setup",
            json={"method": "totp"},
            headers=self.auth_headers
        )
        assert setup_response.status_code == 200
        setup_data = setup_response.json()
        secret_key = setup_data["secret_key"]
        backup_codes = setup_data["backup_codes"]
        
        # Étape 2: Vérifier que le MFA n'est pas encore activé
        status_response = client.get("/api/mfa/status", headers=self.auth_headers)
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["is_setup"] == True
        assert status_data["is_enabled"] == False
        
        # Étape 3: Générer un code TOTP valide (simulation)
        # Note: En vrai, on utiliserait la clé secrète pour générer un code
        # Pour le test, nous simulons un code valide
        from app.services.mfa_service import MFAService
        mfa_service = MFAService(self.db)
        valid_code = mfa_service._generate_totp_code(secret_key, int(datetime.now().timestamp() // 30))
        
        # Étape 4: Vérifier le code de configuration
        verify_response = client.post(
            "/api/mfa/verify",
            json={"code": valid_code},
            headers=self.auth_headers
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["success"] == True
        
        # Étape 5: Vérifier que le MFA est maintenant activé
        status_response = client.get("/api/mfa/status", headers=self.auth_headers)
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["is_enabled"] == True
        
        # Étape 6: Générer de nouveaux codes de récupération
        recovery_response = client.post(
            "/api/mfa/recovery-codes/generate",
            headers=self.auth_headers
        )
        assert recovery_response.status_code == 200
        recovery_data = recovery_response.json()
        assert len(recovery_data["recovery_codes"]) == 10
        
        # Étape 7: Vérifier qu'on peut récupérer les paramètres
        settings_response = client.get("/api/mfa/settings", headers=self.auth_headers)
        assert settings_response.status_code == 200
        settings_data = settings_response.json()
        assert settings_data["is_enabled"] == True
        
        # Étape 8: Vérifier les tentatives enregistrées
        attempts_response = client.get("/api/mfa/attempts", headers=self.auth_headers)
        assert attempts_response.status_code == 200
        attempts_data = attempts_response.json()
        assert len(attempts_data) >= 2  # Au moins setup et enable
        
        print("✅ Workflow MFA complet testé avec succès")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])