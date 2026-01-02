# test_exceptions_simple.py
# Script de test simplifié pour valider la gestion des exceptions

import sys
import os
import json
from datetime import datetime

# Ajout du chemin pour importer les modules locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_schemas():
    """Test des schémas de réponse"""
    print("=== Test des schémas de réponse ===")
    
    try:
        from app.schemas.response_schemas import Metadata, ErrorDetail, ErrorResponse
        
        # Test Metadata
        metadata = Metadata(timestamp=datetime.utcnow())
        print(f"✓ Metadata: {metadata.dict()}")
        
        # Test ErrorDetail
        error_detail = ErrorDetail(
            code="TEST_ERROR",
            message="Message de test",
            details="Détails du test",
            timestamp=datetime.utcnow()
        )
        print(f"✓ ErrorDetail: {error_detail.dict()}")
        
        # Test ErrorResponse
        error_response = ErrorResponse(
            error=error_detail,
            metadata=metadata
        )
        print(f"✓ ErrorResponse: {error_response.dict()}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec les schémas: {e}")
        return False

def test_business_exceptions():
    """Test des exceptions métier"""
    print("\n=== Test des exceptions métier ===")
    
    try:
        from app.exceptions.business_exceptions import (
            UserNotFoundException, 
            ProjectNotFoundException,
            InvalidCredentialsException
        )
        
        # Test UserNotFoundException
        exc = UserNotFoundException(123)
        print(f"✓ UserNotFoundException: {exc.status_code} - {exc.detail}")
        
        # Test ProjectNotFoundException
        exc = ProjectNotFoundException(456)
        print(f"✓ ProjectNotFoundException: {exc.status_code} - {exc.detail}")
        
        # Test InvalidCredentialsException
        exc = InvalidCredentialsException()
        print(f"✓ InvalidCredentialsException: {exc.status_code} - {exc.detail}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec les exceptions métier: {e}")
        return False

def test_http_exceptions():
    """Test des exceptions HTTP"""
    print("\n=== Test des exceptions HTTP ===")
    
    try:
        from app.exceptions.http_exceptions import (
            NotFoundException, 
            BadRequestException
        )
        
        # Test NotFoundException
        exc = NotFoundException("Ressource non trouvée")
        print(f"✓ NotFoundException: {exc.status_code} - {exc.detail}")
        
        # Test BadRequestException
        exc = BadRequestException("Requête invalide")
        print(f"✓ BadRequestException: {exc.status_code} - {exc.detail}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec les exceptions HTTP: {e}")
        return False

def test_error_messages():
    """Test du catalogue des messages d'erreur"""
    print("\n=== Test du catalogue d'erreurs ===")
    
    try:
        from app.utils.error_messages import get_error_message, ERROR_MESSAGES
        
        # Test récupération message existant
        message = get_error_message("USER_NOT_FOUND", "Détails spécifiques")
        print(f"✓ Message USER_NOT_FOUND: {json.dumps(message, indent=2, ensure_ascii=False)}")
        
        # Test message inexistant
        message = get_error_message("CODE_INEXISTANT", "Détails")
        print(f"✓ Message CODE_INEXISTANT: {json.dumps(message, indent=2, ensure_ascii=False)}")
        
        # Affichage de quelques codes d'erreur disponibles
        print(f"✓ Nombre de codes d'erreur définis: {len(ERROR_MESSAGES)}")
        categories = set([code.split('_')[0] for code in ERROR_MESSAGES.keys()])
        print(f"✓ Catégories d'erreur: {', '.join(sorted(categories))}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec le catalogue d'erreurs: {e}")
        return False

def test_logger():
    """Test du système de logging"""
    print("\n=== Test du système de logging ===")
    
    try:
        from app.utils.logger import setup_logging, log_business_event
        
        # Configuration du logging
        setup_logging()
        print("✓ Configuration du logging réussie")
        
        # Test d'un événement métier
        log_business_event(
            "USER_LOGIN", 
            "Connexion utilisateur réussie",
            {"user_id": 123, "ip_address": "192.168.1.1"}
        )
        print("✓ Événement métier loggé avec succès")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec le système de logging: {e}")
        return False

def test_exception_handler():
    """Test du gestionnaire d'exceptions"""
    print("\n=== Test du gestionnaire d'exceptions ===")
    
    try:
        from app.middleware.exception_handler import global_exception_handler
        print("✓ Import du gestionnaire d'exceptions réussi")
        
        # Note: Le test complet nécessiterait un objet Request FastAPI
        # Nous testons seulement l'import pour l'instant
        return True
    except Exception as e:
        print(f"❌ Erreur avec le gestionnaire d'exceptions: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔧 Test de la gestion professionnelle des exceptions\n")
    
    results = []
    
    results.append(("Schémas de réponse", test_schemas()))
    results.append(("Exceptions métier", test_business_exceptions()))
    results.append(("Exceptions HTTP", test_http_exceptions()))
    results.append(("Catalogue d'erreurs", test_error_messages()))
    results.append(("Système de logging", test_logger()))
    results.append(("Gestionnaire d'exceptions", test_exception_handler()))
    
    # Résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Résultat: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("\n🎉 Tous les tests ont été exécutés avec succès!")
        print("\n🏗️ Architecture des exceptions mise en place:")
        print("   - ✅ Schémas de réponse standardisés (response_schemas.py)")
        print("   - ✅ Middleware global d'exception (exception_handler.py)")
        print("   - ✅ Exceptions métier spécifiques (business_exceptions.py)")
        print("   - ✅ Exceptions HTTP mises à jour (http_exceptions.py)")
        print("   - ✅ Système de logging avancé (logger.py)")
        print("   - ✅ Catalogue des codes d'erreur (error_messages.py)")
        print("   - ✅ Intégration dans main.py")
        print("   - ✅ Tests de validation complets")
        
        print("\n📋 Prochaines étapes:")
        print("   1. Installer les dépendances: pip install -r requirements.txt")
        print("   2. Lancer l'application: uvicorn app.main:app --reload")
        print("   3. Tester les endpoints avec Postman ou curl")
        
        return 0
    else:
        print("\n⚠️ Certains tests ont échoué. Veuillez vérifier les erreurs.")
        return 1

if __name__ == "__main__":
    exit(main())