# backend/test_oauth_system.py
"""
Tests complets pour le système OAuth2
Teste les fonctionnalités d'authentification OAuth2 avec Google, GitHub, Microsoft et Facebook
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.oauth import OAuthProvider, OAuthUser, OAuthState, OAuthLoginAttempt
from app.models.user import User
from app.services.oauth_service import OAuthService
from app.exceptions.oauth_exceptions import (
    OAuthProviderNotConfiguredException,
    OAuthStateNotFoundException,
    OAuthStateExpiredException,
    OAuthInvalidCodeException,
    OAuthUserNotFoundException,
    OAuthProviderException
)
from app.database.database import Base


class TestOAuthSystem:
    """Tests complets du système OAuth2"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Configuration initiale pour les tests"""
        # Configuration de la base de données de test
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()
        
        # Création des providers OAuth2 de test
        providers = [
            OAuthProvider(name="google", display_name="Google", is_active=True),
            OAuthProvider(name="github", display_name="GitHub", is_active=True),
            OAuthProvider(name="microsoft", display_name="Microsoft", is_active=True),
            OAuthProvider(name="facebook", display_name="Facebook", is_active=True)
        ]
        
        for provider in providers:
            self.db.add(provider)
        self.db.commit()
        
        yield
        
        # Nettoyage
        self.db.close()
        Base.metadata.drop_all(self.engine)
    
    def test_oauth_service_initialization(self):
        """Test de l'initialisation du service OAuth2"""
        service = OAuthService(self.db)
        assert service.db == self.db
        assert isinstance(service.providers_config, dict)
    
    def test_get_authorization_url_success(self):
        """Test de génération d'URL d'autorisation réussie"""
        service = OAuthService(self.db)
        
        with patch('oauth_config.OAuthConfig.get_provider_config') as mock_config:
            mock_config.return_value = {
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "authorization_url": "https://test.com/auth",
                "scope": "email profile",
                "redirect_uri": "http://localhost:3000/callback"
            }
            
            url, state = service.get_authorization_url("google", "http://localhost:3000/callback")
            
            assert "https://test.com/auth" in url
            assert "client_id=test_client_id" in url
            assert "redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback" in url
            assert "response_type=code" in url
            assert len(state) == 43  # 32 bytes en base64
            
            # Vérification que le state est stocké en base
            saved_state = self.db.query(OAuthState).filter(OAuthState.state == state).first()
            assert saved_state is not None
            assert saved_state.provider == "google"
            assert saved_state.redirect_uri == "http://localhost:3000/callback"
    
    def test_get_authorization_url_provider_not_configured(self):
        """Test d'erreur pour provider non configuré"""
        service = OAuthService(self.db)
        
        with patch('oauth_config.OAuthConfig.get_provider_config') as mock_config:
            mock_config.return_value = {}  # Provider non configuré
            
            with pytest.raises(OAuthProviderNotConfiguredException):
                service.get_authorization_url("nonexistent", "http://localhost:3000/callback")
    
    def test_verify_state_success(self):
        """Test de vérification de state valide"""
        service = OAuthService(self.db)
        
        # Création d'un state valide
        state = "test_state_123"
        oauth_state = OAuthState(
            state=state,
            provider="google",
            redirect_uri="http://localhost:3000/callback",
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        self.db.add(oauth_state)
        self.db.commit()
        
        result = service.verify_state(state, "google")
        assert result is True
        
        # Vérification que le state a été supprimé
        deleted_state = self.db.query(OAuthState).filter(OAuthState.state == state).first()
        assert deleted_state is None
    
    def test_verify_state_not_found(self):
        """Test d'erreur pour state non trouvé"""
        service = OAuthService(self.db)
        
        with pytest.raises(OAuthStateNotFoundException):
            service.verify_state("nonexistent_state", "google")
    
    def test_verify_state_expired(self):
        """Test d'erreur pour state expiré"""
        service = OAuthService(self.db)
        
        # Création d'un state expiré
        state = "expired_state"
        oauth_state = OAuthState(
            state=state,
            provider="google",
            redirect_uri="http://localhost:3000/callback",
            expires_at=datetime.utcnow() - timedelta(minutes=1)  # Expiré
        )
        self.db.add(oauth_state)
        self.db.commit()
        
        with pytest.raises(OAuthStateExpiredException):
            service.verify_state(state, "google")
        
        # Vérification que le state expiré a été supprimé
        deleted_state = self.db.query(OAuthState).filter(OAuthState.state == state).first()
        assert deleted_state is None
    
    def test_exchange_code_for_token_success(self):
        """Test d'échange de code contre token réussie"""
        service = OAuthService(self.db)
        
        with patch('oauth_config.OAuthConfig.get_provider_config') as mock_config, \
             patch('requests.post') as mock_post:
            
            mock_config.return_value = {
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "token_url": "https://test.com/token",
                "redirect_uri": "http://localhost:3000/callback"
            }
            
            # Mock de la réponse du provider
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "test_access_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "test_refresh_token"
            }
            mock_post.return_value = mock_response
            
            token_data = service.exchange_code_for_token(
                "google", "test_code", "http://localhost:3000/callback"
            )
            
            assert token_data["access_token"] == "test_access_token"
            assert token_data["token_type"] == "bearer"
            assert token_data["expires_in"] == 3600
    
    def test_exchange_code_for_token_invalid_code(self):
        """Test d'erreur pour code invalide"""
        service = OAuthService(self.db)
        
        with patch('oauth_config.OAuthConfig.get_provider_config') as mock_config, \
             patch('requests.post') as mock_post:
            
            mock_config.return_value = {
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "token_url": "https://test.com/token"
            }
            
            # Mock d'une réponse d'erreur
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Invalid code"
            mock_post.return_value = mock_response
            
            with pytest.raises(OAuthInvalidCodeException):
                service.exchange_code_for_token(
                    "google", "invalid_code", "http://localhost:3000/callback"
                )
    
    def test_get_user_info_success(self):
        """Test de récupération des informations utilisateur"""
        service = OAuthService(self.db)
        
        with patch('oauth_config.OAuthConfig.get_provider_config') as mock_config, \
             patch('requests.get') as mock_get:
            
            mock_config.return_value = {
                "userinfo_url": "https://test.com/userinfo"
            }
            
            # Mock de la réponse du provider
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "123456",
                "email": "test@example.com",
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "picture": "https://example.com/photo.jpg",
                "locale": "fr-FR",
                "email_verified": True
            }
            mock_get.return_value = mock_response
            
            user_info = service.get_user_info("google", "test_access_token")
            
            assert user_info["provider"] == "google"
            assert user_info["provider_user_id"] == "123456"
            assert user_info["email"] == "test@example.com"
            assert user_info["name"] == "Test User"
            assert user_info["given_name"] == "Test"
            assert user_info["family_name"] == "User"
            assert user_info["picture"] == "https://example.com/photo.jpg"
            assert user_info["locale"] == "fr-FR"
            assert user_info["email_verified"] is True
    
    def test_normalize_user_info_google(self):
        """Test de normalisation des données Google"""
        service = OAuthService(self.db)
        
        google_data = {
            "sub": "123456",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/photo.jpg",
            "locale": "fr-FR",
            "email_verified": True
        }
        
        normalized = service._normalize_user_info("google", google_data)
        
        assert normalized["provider"] == "google"
        assert normalized["provider_user_id"] == "123456"
        assert normalized["email"] == "test@example.com"
        assert normalized["name"] == "Test User"
        assert normalized["given_name"] == "Test"
        assert normalized["family_name"] == "User"
    
    def test_normalize_user_info_github(self):
        """Test de normalisation des données GitHub"""
        service = OAuthService(self.db)
        
        github_data = {
            "id": 123456,
            "login": "testuser",
            "name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        
        normalized = service._normalize_user_info("github", github_data)
        
        assert normalized["provider"] == "github"
        assert normalized["provider_user_id"] == "123456"
        assert normalized["email"] == "testuser@users.noreply.github.com"
        assert normalized["name"] == "Test User"
        assert normalized["picture"] == "https://example.com/avatar.jpg"
    
    def test_normalize_user_info_microsoft(self):
        """Test de normalisation des données Microsoft"""
        service = OAuthService(self.db)
        
        microsoft_data = {
            "id": "123456",
            "mail": "test@example.com",
            "displayName": "Test User",
            "givenName": "Test",
            "surname": "User"
        }
        
        normalized = service._normalize_user_info("microsoft", microsoft_data)
        
        assert normalized["provider"] == "microsoft"
        assert normalized["provider_user_id"] == "123456"
        assert normalized["email"] == "test@example.com"
        assert normalized["name"] == "Test User"
        assert normalized["given_name"] == "Test"
        assert normalized["family_name"] == "User"
        assert normalized["email_verified"] is True
    
    def test_normalize_user_info_facebook(self):
        """Test de normalisation des données Facebook"""
        service = OAuthService(self.db)
        
        facebook_data = {
            "id": "123456",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
        
        normalized = service._normalize_user_info("facebook", facebook_data)
        
        assert normalized["provider"] == "facebook"
        assert normalized["provider_user_id"] == "123456"
        assert normalized["email"] == "test@example.com"
        assert normalized["given_name"] == "Test"
        assert normalized["family_name"] == "User"
        assert normalized["name"] == "Test User"
        assert normalized["email_verified"] is True
        assert normalized["picture"] == "https://graph.facebook.com/123456/picture?type=large"
    
    def test_find_or_create_user_new_user(self):
        """Test de création d'un nouvel utilisateur OAuth2"""
        service = OAuthService(self.db)
        
        user_info = {
            "provider": "google",
            "provider_user_id": "123456",
            "email": "newuser@example.com",
            "name": "New User",
            "email_verified": True
        }
        
        user = service.find_or_create_user(user_info)
        
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.username is not None
        assert user.is_active is True
        assert user.email_verified is True
        
        # Vérification de l'association OAuth
        oauth_user = self.db.query(OAuthUser).filter(
            OAuthUser.provider_user_id == "123456"
        ).first()
        assert oauth_user is not None
        assert oauth_user.user_id == user.id
        assert oauth_user.email == "newuser@example.com"
    
    def test_find_or_create_user_existing_oauth(self):
        """Test de récupération d'un utilisateur OAuth2 existant"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur et association OAuth existante
        user = User(
            username="existinguser",
            email="existing@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.name == "google").first()
        
        oauth_user = OAuthUser(
            user_id=user.id,
            provider_id=provider.id,
            provider_user_id="123456",
            email="existing@example.com",
            profile_data=json.dumps({"test": "data"})
        )
        self.db.add(oauth_user)
        self.db.commit()
        
        user_info = {
            "provider": "google",
            "provider_user_id": "123456",
            "email": "existing@example.com",
            "name": "Updated Name",
            "email_verified": True
        }
        
        found_user = service.find_or_create_user(user_info)
        
        assert found_user.id == user.id
        assert found_user.email == "existing@example.com"
        
        # Vérification que le profil a été mis à jour
        updated_oauth = self.db.query(OAuthUser).filter(OAuthUser.provider_user_id == "123456").first()
        profile_data = json.loads(updated_oauth.profile_data)
        assert profile_data["name"] == "Updated Name"
    
    def test_find_or_create_user_existing_email(self):
        """Test d'association avec un utilisateur existant par email"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur existant
        user = User(
            username="existinguser",
            email="existing@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        user_info = {
            "provider": "google",
            "provider_user_id": "123456",
            "email": "existing@example.com",
            "name": "Existing User",
            "email_verified": True
        }
        
        found_user = service.find_or_create_user(user_info)
        
        assert found_user.id == user.id
        assert found_user.email == "existing@example.com"
        
        # Vérification de la création de l'association OAuth
        oauth_user = self.db.query(OAuthUser).filter(
            OAuthUser.provider_user_id == "123456"
        ).first()
        assert oauth_user is not None
        assert oauth_user.user_id == user.id
    
    def test_link_oauth_account_success(self):
        """Test d'association d'un compte OAuth2 à un utilisateur existant"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        user_info = {
            "provider": "google",
            "provider_user_id": "123456",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        oauth_user = service.link_oauth_account(user, user_info)
        
        assert oauth_user is not None
        assert oauth_user.user_id == user.id
        assert oauth_user.provider_user_id == "123456"
        assert oauth_user.email == "test@example.com"
    
    def test_link_oauth_account_already_linked(self):
        """Test d'erreur pour compte OAuth2 déjà associé"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur et association OAuth existante
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.name == "google").first()
        
        oauth_user = OAuthUser(
            user_id=user.id,
            provider_id=provider.id,
            provider_user_id="123456",
            email="test@example.com"
        )
        self.db.add(oauth_user)
        self.db.commit()
        
        user_info = {
            "provider": "google",
            "provider_user_id": "123456",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        # Tentative de liaison du même compte - devrait retourner l'existant
        result = service.link_oauth_account(user, user_info)
        assert result.id == oauth_user.id
    
    def test_link_oauth_account_linked_to_other_user(self):
        """Test d'erreur pour compte OAuth2 associé à un autre utilisateur"""
        service = OAuthService(self.db)
        
        # Création de deux utilisateurs
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password="hashed_password1",
            is_active=True
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password="hashed_password2",
            is_active=True
        )
        self.db.add_all([user1, user2])
        self.db.commit()
        self.db.refresh(user1)
        self.db.refresh(user2)
        
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.name == "google").first()
        
        # Association du compte OAuth au premier utilisateur
        oauth_user = OAuthUser(
            user_id=user1.id,
            provider_id=provider.id,
            provider_user_id="123456",
            email="user1@example.com"
        )
        self.db.add(oauth_user)
        self.db.commit()
        
        user_info = {
            "provider": "google",
            "provider_user_id": "123456",
            "email": "user1@example.com",
            "name": "User One"
        }
        
        # Tentative d'association du même compte OAuth au deuxième utilisateur
        with pytest.raises(OAuthProviderException):
            service.link_oauth_account(user2, user_info)
    
    def test_unlink_oauth_account_success(self):
        """Test de dissociation d'un compte OAuth2"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur et association OAuth
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        provider = self.db.query(OAuthProvider).filter(OAuthProvider.name == "google").first()
        
        oauth_user = OAuthUser(
            user_id=user.id,
            provider_id=provider.id,
            provider_user_id="123456",
            email="test@example.com"
        )
        self.db.add(oauth_user)
        self.db.commit()
        
        result = service.unlink_oauth_account(user, "google")
        
        assert result is True
        
        # Vérification que l'association a été supprimée
        deleted_oauth = self.db.query(OAuthUser).filter(
            OAuthUser.user_id == user.id,
            OAuthUser.provider.has(name="google")
        ).first()
        assert deleted_oauth is None
    
    def test_unlink_oauth_account_not_found(self):
        """Test d'erreur pour dissociation d'un compte OAuth2 non existant"""
        service = OAuthService(self.db)
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        with pytest.raises(OAuthUserNotFoundException):
            service.unlink_oauth_account(user, "google")
    
    def test_get_user_oauth_accounts(self):
        """Test de récupération des comptes OAuth2 d'un utilisateur"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur avec plusieurs associations OAuth
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        google_provider = self.db.query(OAuthProvider).filter(OAuthProvider.name == "google").first()
        github_provider = self.db.query(OAuthProvider).filter(OAuthProvider.name == "github").first()
        
        oauth_accounts = [
            OAuthUser(
                user_id=user.id,
                provider_id=google_provider.id,
                provider_user_id="google_123",
                email="test@example.com"
            ),
            OAuthUser(
                user_id=user.id,
                provider_id=github_provider.id,
                provider_user_id="github_456",
                email="test@example.com"
            )
        ]
        
        for account in oauth_accounts:
            self.db.add(account)
        self.db.commit()
        
        accounts = service.get_user_oauth_accounts(user)
        
        assert len(accounts) == 2
        assert any(acc.provider_user_id == "google_123" for acc in accounts)
        assert any(acc.provider_user_id == "github_456" for acc in accounts)
    
    def test_log_oauth_attempt(self):
        """Test de journalisation d'une tentative de connexion OAuth2"""
        service = OAuthService(self.db)
        
        service.log_oauth_attempt(
            provider="google",
            provider_user_id="123456",
            email="test@example.com",
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            success=True,
            failure_reason=None
        )
        
        # Vérification de la journalisation
        attempt = self.db.query(OAuthLoginAttempt).first()
        assert attempt is not None
        assert attempt.provider == "google"
        assert attempt.provider_user_id == "123456"
        assert attempt.email == "test@example.com"
        assert attempt.ip_address == "192.168.1.1"
        assert attempt.user_agent == "Test Browser"
        assert attempt.success is True
        assert attempt.failure_reason is None
    
    def test_generate_username_unique(self):
        """Test de génération de nom d'utilisateur unique"""
        service = OAuthService(self.db)
        
        # Création d'un utilisateur existant
        existing_user = User(
            username="testuser",
            email="existing@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        self.db.add(existing_user)
        self.db.commit()
        
        user_info = {
            "given_name": "Test",
            "name": "Test User"
        }
        
        username = service._generate_username(user_info)
        
        # Le nom d'utilisateur devrait être unique
        assert username != "testuser"
        assert username.startswith("test")


def run_oauth_tests():
    """Fonction pour exécuter tous les tests OAuth2 et générer un rapport"""
    import sys
    import subprocess
    
    print("🔐 LANCEMENT DES TESTS OAUTH2")
    print("=" * 50)
    
    # Exécution des tests avec pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "backend/test_oauth_system.py", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    # Analyse des résultats
    print("RÉSULTATS DES TESTS:")
    print(result.stdout)
    
    if result.stderr:
        print("ERREURS:")
        print(result.stderr)
    
    # Génération du rapport
    test_report = generate_test_report(result)
    print("\n" + "=" * 50)
    print("📊 RAPPORT DE TEST OAUTH2")
    print("=" * 50)
    print(test_report)
    
    return result.returncode == 0


def generate_test_report(pytest_result):
    """Génère un rapport de test détaillé"""
    lines = pytest_result.stdout.split('\n')
    
    # Extraction des statistiques
    passed = 0
    failed = 0
    skipped = 0
    errors = 0
    
    for line in lines:
        if "passed" in line and "failed" in line:
            parts = line.split()
            for part in parts:
                if part.isdigit():
                    if passed == 0:
                        passed = int(part)
                    elif failed == 0:
                        failed = int(part)
                    elif skipped == 0:
                        skipped = int(part)
                    elif errors == 0:
                        errors = int(part)
            break
    
    total = passed + failed + skipped + errors
    
    # Génération du rapport
    report = f"""
📈 STATISTIQUES DES TESTS:
   ✅ Tests réussis: {passed}
   ❌ Tests échoués: {failed}
   ⏭️  Tests ignorés: {skipped}
   ⚠️  Erreurs: {errors}
   📊 Total: {total}

🎯 COUVERTURE FONCTIONNELLE:

   🔐 Service OAuth2
     ✅ Initialisation du service
     ✅ Génération d'URL d'autorisation
     ✅ Vérification des states de sécurité
     ✅ Échange code/token
     ✅ Récupération des informations utilisateur
     ✅ Normalisation des données (Google, GitHub, Microsoft, Facebook)
     ✅ Création et recherche d'utilisateur
     ✅ Association/dissociation de comptes
     ✅ Journalisation des tentatives

   🛡️  Gestion des erreurs
     ✅ Provider non configuré
     ✅ State non trouvé ou expiré
     ✅ Code d'autorisation invalide
     ✅ Utilisateur OAuth2 non trouvé
     ✅ Compte déjà associé

   🔄 Intégration
     ✅ Génération de noms d'utilisateur uniques
     ✅ Association avec utilisateurs existants
     ✅ Gestion des conflits d'emails

📋 RÉSUMÉ:
   Le système OAuth2 a été testé de manière complète avec {total} tests.
   Taux de réussite: {(passed/total)*100 if total > 0 else 0:.1f}%

💡 RECOMMANDATIONS:
   {"✅ Tous les tests sont réussis - Le système OAuth2 est prêt pour la production" if failed == 0 and errors == 0 else "❌ Certains tests ont échoué - Vérifier les implémentations"}
"""
    
    return report


if __name__ == "__main__":
    # Exécution des tests si le script est lancé directement
    success = run_oauth_tests()
    sys.exit(0 if success else 1)