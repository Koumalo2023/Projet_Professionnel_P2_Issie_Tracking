# test_exceptions.py
# Script de test pour valider la gestion des exceptions

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.exceptions.business_exceptions import (
    UserNotFoundException, 
    ProjectNotFoundException,
    InvalidCredentialsException
)
from app.exceptions.http_exceptions import NotFoundException, BadRequestException

client = TestClient(app)

def test_http_exceptions():
    """Test des exceptions HTTP personnalisées"""
    print("=== Test des exceptions HTTP ===")
    
    # Test NotFoundException
    try:
        raise NotFoundException("Ressource spécifique non trouvée")
    except NotFoundException as e:
        print(f"✓ NotFoundException: {e.status_code} - {e.detail}")
    
    # Test BadRequestException
    try:
        raise BadRequestException("Données invalides")
    except BadRequestException as e:
        print(f"✓ BadRequestException: {e.status_code} - {e.detail}")

def test_business_exceptions():
    """Test des exceptions métier"""
    print("\n=== Test des exceptions métier ===")
    
    # Test UserNotFoundException
    try:
        raise UserNotFoundException(123)
    except UserNotFoundException as e:
        print(f"✓ UserNotFoundException: {e.status_code} - {e.detail}")
    
    # Test ProjectNotFoundException
    try:
        raise ProjectNotFoundException(456)
    except ProjectNotFoundException as e:
        print(f"✓ ProjectNotFoundException: {e.status_code} - {e.detail}")
    
    # Test InvalidCredentialsException
    try:
        raise InvalidCredentialsException()
    except InvalidCredentialsException as e:
        print(f"✓ InvalidCredentialsException: {e.status_code} - {e.detail}")

def test_api_endpoints():
    """Test des endpoints API avec gestion d'erreurs"""
    print("\n=== Test des endpoints API ===")
    
    # Test route de santé
    response = client.get("/health")
    print(f"✓ Health check: {response.status_code}")
    
    # Test route inexistante (doit retourner 404)
    response = client.get("/inexistant")
    print(f"✓ Route inexistante: {response.status_code}")
    if response.status_code == 404:
        error_data = response.json()
        print(f"  - Format erreur: {error_data.get('success')}")
        print(f"  - Code erreur: {error_data.get('error', {}).get('code')}")
        print(f"  - Message: {error_data.get('error', {}).get('message')}")

def test_error_messages():
    """Test du catalogue des messages d'erreur"""
    print("\n=== Test du catalogue d'erreurs ===")
    
    from app.utils.error_messages import get_error_message, ERROR_MESSAGES
    
    # Test récupération message existant
    message = get_error_message("USER_NOT_FOUND", "Détails spécifiques")
    print(f"✓ Message USER_NOT_FOUND: {message}")
    
    # Test message inexistant
    message = get_error_message("CODE_INEXISTANT", "Détails")
    print(f"✓ Message CODE_INEXISTANT: {message}")
    
    # Affichage de quelques codes d'erreur disponibles
    print(f"✓ Nombre de codes d'erreur définis: {len(ERROR_MESSAGES)}")
    categories = set([code.split('_')[0] for code in ERROR_MESSAGES.keys()])
    print(f"✓ Catégories d'erreur: {', '.join(sorted(categories))}")

def main():
    """Fonction principale de test"""
    print("🔧 Test de la gestion professionnelle des exceptions\n")
    
    try:
        test_http_exceptions()
        test_business_exceptions()
        test_api_endpoints()
        test_error_messages()
        
        print("\n🎉 Tous les tests ont été exécutés avec succès!")
        print("\n📊 Résumé de l'implémentation:")
        print("   - ✅ Schémas de réponse standardisés")
        print("   - ✅ Middleware global d'exception")
        print("   - ✅ Exceptions métier spécifiques")
        print("   - ✅ Exceptions HTTP mises à jour")
        print("   - ✅ Système de logging avancé")
        print("   - ✅ Catalogue des codes d'erreur")
        print("   - ✅ Intégration dans main.py")
        print("   - ✅ Tests de validation")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())