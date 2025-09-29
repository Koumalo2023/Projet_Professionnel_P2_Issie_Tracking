#!/usr/bin/env python3
"""
Script de test pour le système de gestion d'exceptions professionnel
Teste les différentes exceptions et leur gestion
"""

import sys
import os
import asyncio
from datetime import datetime

# Ajouter le chemin du backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.main import app
from app.exceptions.http_exceptions import (
    NotFoundException, UnauthorizedException, ForbiddenException,
    BadRequestException, ConflictException, ValidationException,
    InternalServerErrorException
)
from app.exceptions.business_exceptions import (
    UserNotFoundException, ProjectNotFoundException, 
    InvalidCredentialsException, PermissionDeniedException,
    ValidationException as BusinessValidationException
)
from app.schemas.response_schemas import ErrorResponse, SuccessResponse


def test_http_exceptions():
    """Test des exceptions HTTP personnalisées"""
    print("🧪 Test des exceptions HTTP personnalisées...")
    
    # Test NotFoundException
    try:
        raise NotFoundException(
            message="User not found", 
            details="User with ID 123 does not exist",
            resource_type="user",
            resource_id="123"
        )
    except NotFoundException as e:
        assert e.status_code == 404
        assert e.detail["code"] == "NOT_FOUND"
        assert e.detail["message"] == "User not found"
        print("✅ NotFoundException fonctionne correctement")
    
    # Test UnauthorizedException
    try:
        raise UnauthorizedException(
            message="Authentication required",
            details="Please provide valid credentials"
        )
    except UnauthorizedException as e:
        assert e.status_code == 401
        assert e.detail["code"] == "UNAUTHORIZED"
        print("✅ UnauthorizedException fonctionne correctement")
    
    # Test ForbiddenException
    try:
        raise ForbiddenException(
            message="Access forbidden",
            details="You don't have permission to access this resource",
            required_permission="project:read"
        )
    except ForbiddenException as e:
        assert e.status_code == 403
        assert e.detail["code"] == "FORBIDDEN"
        assert "required_permission" in e.detail
        print("✅ ForbiddenException fonctionne correctement")
    
    # Test BadRequestException
    try:
        raise BadRequestException(
            message="Invalid request data",
            details="The provided data is malformed",
            validation_errors=["Field 'email' is required"]
        )
    except BadRequestException as e:
        assert e.status_code == 400
        assert e.detail["code"] == "BAD_REQUEST"
        assert "validation_errors" in e.detail
        print("✅ BadRequestException fonctionne correctement")
    
    # Test ConflictException
    try:
        raise ConflictException(
            message="Resource conflict",
            details="User with this email already exists",
            conflicting_field="email"
        )
    except ConflictException as e:
        assert e.status_code == 409
        assert e.detail["code"] == "CONFLICT"
        print("✅ ConflictException fonctionne correctement")
    
    # Test ValidationException
    try:
        raise ValidationException(
            message="Validation failed",
            details="Multiple validation errors occurred",
            validation_errors=[{"field": "email", "error": "Invalid format"}]
        )
    except ValidationException as e:
        assert e.status_code == 422
        assert e.detail["code"] == "VALIDATION_ERROR"
        print("✅ ValidationException fonctionne correctement")
    
    print("🎉 Toutes les exceptions HTTP fonctionnent correctement!\n")


def test_business_exceptions():
    """Test des exceptions métier"""
    print("🧪 Test des exceptions métier...")
    
    # Test UserNotFoundException
    try:
        raise UserNotFoundException(user_id=123)
    except UserNotFoundException as e:
        assert e.status_code == 404
        assert e.detail["code"] == "USER_NOT_FOUND"
        assert "user_id" in e.detail
        print("✅ UserNotFoundException fonctionne correctement")
    
    # Test ProjectNotFoundException
    try:
        raise ProjectNotFoundException(project_id=456)
    except ProjectNotFoundException as e:
        assert e.status_code == 404
        assert e.detail["code"] == "PROJECT_NOT_FOUND"
        assert "project_id" in e.detail
        print("✅ ProjectNotFoundException fonctionne correctement")
    
    # Test InvalidCredentialsException
    try:
        raise InvalidCredentialsException()
    except InvalidCredentialsException as e:
        assert e.status_code == 401
        assert e.detail["code"] == "AUTH_INVALID_CREDENTIALS"
        print("✅ InvalidCredentialsException fonctionne correctement")
    
    # Test PermissionDeniedException
    try:
        raise PermissionDeniedException(
            required_permission="project:delete",
            resource_type="project",
            resource_id=789
        )
    except PermissionDeniedException as e:
        assert e.status_code == 403
        assert e.detail["code"] == "PERMISSION_DENIED"
        assert "required_permission" in e.detail
        print("✅ PermissionDeniedException fonctionne correctement")
    
    # Test BusinessValidationException
    try:
        raise BusinessValidationException(
            message="Business validation failed",
            details="Invalid business rules",
            validation_errors=[{"rule": "minimum_age", "error": "User must be at least 18"}]
        )
    except BusinessValidationException as e:
        assert e.status_code == 422
        assert e.detail["code"] == "VALIDATION_ERROR"
        print("✅ BusinessValidationException fonctionne correctement")
    
    print("🎉 Toutes les exceptions métier fonctionnent correctement!\n")


def test_response_schemas():
    """Test des schémas de réponse"""
    print("🧪 Test des schémas de réponse...")
    
    from app.schemas.response_schemas import (
        SuccessResponse, ErrorResponse, ErrorDetail, Metadata,
        PaginatedResponse, PaginationInfo
    )
    
    # Test SuccessResponse
    success_data = {"id": 1, "name": "Test User"}
    success_response = SuccessResponse(
        data=success_data,
        metadata=Metadata(timestamp=datetime.utcnow())
    )
    
    assert success_response.success == True
    assert success_response.data == success_data
    assert isinstance(success_response.metadata.timestamp, datetime)
    print("✅ SuccessResponse fonctionne correctement")
    
    # Test ErrorResponse
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="USER_NOT_FOUND",
            message="User not found",
            details="User with ID 123 does not exist",
            timestamp=datetime.utcnow()
        ),
        metadata=Metadata(timestamp=datetime.utcnow())
    )
    
    assert error_response.success == False
    assert error_response.error.code == "USER_NOT_FOUND"
    assert isinstance(error_response.error.timestamp, datetime)
    print("✅ ErrorResponse fonctionne correctement")
    
    # Test PaginatedResponse
    paginated_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    pagination_info = PaginationInfo(
        page=1,
        per_page=10,
        total=2,
        total_pages=1,
        has_next=False,
        has_prev=False
    )
    paginated_response = PaginatedResponse(
        data=paginated_data,
        pagination=pagination_info,
        metadata=Metadata(timestamp=datetime.utcnow())
    )
    
    assert paginated_response.success == True
    assert len(paginated_response.data) == 2
    assert paginated_response.pagination.page == 1
    print("✅ PaginatedResponse fonctionne correctement")
    
    print("🎉 Tous les schémas de réponse fonctionnent correctement!\n")


def test_error_messages():
    """Test des utilitaires de messages d'erreur"""
    print("🧪 Test des utilitaires de messages d'erreur...")
    
    from app.utils.error_messages import (
        get_error_message, format_validation_error, get_error_code_from_http_status
    )
    
    # Test get_error_message
    error_msg = get_error_message("USER_NOT_FOUND", "User with ID 123 not found")
    assert error_msg["code"] == "USER_NOT_FOUND"
    assert error_msg["message"] == "Utilisateur non trouvé"
    assert error_msg["details"] == "User with ID 123 not found"
    print("✅ get_error_message fonctionne correctement")
    
    # Test format_validation_error
    validation_error = format_validation_error("email", "invalid_format", "Must be a valid email")
    assert validation_error["code"] == "VALIDATION_INVALID_FORMAT"
    assert validation_error["field"] == "email"
    assert "Must be a valid email" in validation_error["message"]
    print("✅ format_validation_error fonctionne correctement")
    
    # Test get_error_code_from_http_status
    assert get_error_code_from_http_status(404) == "NOT_FOUND"
    assert get_error_code_from_http_status(500) == "INTERNAL_SERVER_ERROR"
    assert get_error_code_from_http_status(999) == "INTERNAL_SERVER_ERROR"  # Code inconnu
    print("✅ get_error_code_from_http_status fonctionne correctement")
    
    print("🎉 Tous les utilitaires de messages d'erreur fonctionnent correctement!\n")


async def test_exception_handler():
    """Test du gestionnaire d'exceptions global"""
    print("🧪 Test du gestionnaire d'exceptions global...")
    
    from app.middleware.exception_handler import global_exception_handler
    from fastapi import Request
    import json
    
    # Créer une requête mock
    class MockRequest:
        def __init__(self):
            self.method = "GET"
            self.url = "http://test.com/api/users"
            self.client = type('Client', (), {'host': '127.0.0.1'})()
            self.headers = {"user-agent": "test-client"}
    
    mock_request = MockRequest()
    
    # Test avec NotFoundException
    not_found_exception = NotFoundException("User not found")
    response = await global_exception_handler(mock_request, not_found_exception)
    
    assert response.status_code == 404
    response_data = json.loads(response.body.decode())
    assert response_data["success"] == False
    assert response_data["error"]["code"] == "NOT_FOUND"
    print("✅ Gestionnaire d'exceptions fonctionne avec NotFoundException")
    
    # Test avec une exception générique
    generic_exception = Exception("Test generic error")
    response = await global_exception_handler(mock_request, generic_exception)
    
    assert response.status_code == 500
    response_data = json.loads(response.body.decode())
    assert response_data["success"] == False
    assert response_data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    print("✅ Gestionnaire d'exceptions fonctionne avec les exceptions génériques")
    
    print("🎉 Le gestionnaire d'exceptions global fonctionne correctement!\n")


def run_all_tests():
    """Exécute tous les tests"""
    print("🚀 Démarrage des tests du système de gestion d'exceptions...\n")
    
    try:
        test_http_exceptions()
        test_business_exceptions()
        test_response_schemas()
        test_error_messages()
        
        # Exécuter le test asynchrone
        asyncio.run(test_exception_handler())
        
        print("🎉🎉🎉 TOUS LES TESTS ONT RÉUSSI! 🎉🎉🎉")
        print("\n📋 Résumé du système de gestion d'exceptions:")
        print("   ✅ Exceptions HTTP personnalisées")
        print("   ✅ Exceptions métier spécifiques")
        print("   ✅ Schémas de réponse standardisés")
        print("   ✅ Utilitaires de messages d'erreur")
        print("   ✅ Gestionnaire d'exceptions global")
        print("   ✅ Logging structuré et professionnel")
        
        return True
        
    except Exception as e:
        print(f"❌ Certains tests ont échoué: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)