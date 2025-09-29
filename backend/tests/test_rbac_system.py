# tests/test_rbac_system.py
"""
Tests du système RBAC
Vérifie le bon fonctionnement des permissions, rôles et autorisations
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User
from app.models.role import Role, Permission, UserRole, ProjectRole
from app.models.project import Project
from app.auth.auth_utils import create_access_token


# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="module")
def test_db():
    """Fixture pour la base de données de test"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Créer les tables de test
    Base.metadata.create_all(bind=engine)
    
    return TestingSessionLocal


@pytest.fixture(scope="module")
def client():
    """Fixture pour le client de test"""
    def override_get_db():
        """Override de la dépendance de base de données pour les tests"""
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_data(test_db):
    """Fixture pour les données de test"""
    db = test_db()
    
    # Nettoyer les tables
    db.query(ProjectRole).delete()
    db.query(UserRole).delete()
    db.query(Permission).delete()
    db.query(Role).delete()
    db.query(Project).delete()
    db.query(User).delete()
    db.commit()
    
    # Créer des utilisateurs de test
    admin_user = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password="hashed_password"
    )
    db.add(admin_user)
    
    manager_user = User(
        username="manager_test",
        email="manager@test.com",
        hashed_password="hashed_password"
    )
    db.add(manager_user)
    
    developer_user = User(
        username="developer_test",
        email="developer@test.com",
        hashed_password="hashed_password"
    )
    db.add(developer_user)
    
    viewer_user = User(
        username="viewer_test",
        email="viewer@test.com",
        hashed_password="hashed_password"
    )
    db.add(viewer_user)
    
    db.commit()
    
    # Créer des rôles de test
    super_admin_role = Role(name="super_admin", description="Super Admin", is_system_role=True)
    admin_role = Role(name="admin", description="Admin", is_system_role=True)
    project_owner_role = Role(name="project_owner", description="Propriétaire", is_system_role=False)
    developer_role = Role(name="developer", description="Développeur", is_system_role=False)
    viewer_role = Role(name="viewer", description="Observateur", is_system_role=False)
    
    db.add_all([super_admin_role, admin_role, project_owner_role, developer_role, viewer_role])
    db.commit()
    
    # Créer des permissions de test
    project_create_perm = Permission(name="project_create", resource="project", action="create", description="Créer projet")
    project_read_perm = Permission(name="project_read", resource="project", action="read", description="Lire projet")
    project_update_perm = Permission(name="project_update", resource="project", action="update", description="Modifier projet")
    project_delete_perm = Permission(name="project_delete", resource="project", action="delete", description="Supprimer projet")
    
    db.add_all([project_create_perm, project_read_perm, project_update_perm, project_delete_perm])
    db.commit()
    
    # Assigner des permissions aux rôles
    super_admin_role.permissions.extend([
        project_create_perm, project_read_perm, project_update_perm, project_delete_perm
    ])
    
    admin_role.permissions.extend([
        project_create_perm, project_read_perm, project_update_perm
    ])
    
    project_owner_role.permissions.extend([
        project_read_perm, project_update_perm, project_delete_perm
    ])
    
    developer_role.permissions.extend([project_read_perm])
    viewer_role.permissions.extend([project_read_perm])
    
    db.commit()
    
    # Assigner des rôles aux utilisateurs
    db.add(UserRole(user_id=admin_user.id, role_id=super_admin_role.id))
    db.add(UserRole(user_id=manager_user.id, role_id=admin_role.id))
    
    # Créer un projet de test
    test_project = Project(
        name="Projet Test",
        description="Description du projet test",
        type="software"
    )
    db.add(test_project)
    db.commit()
    
    # Assigner des rôles projet
    db.add(ProjectRole(
        user_id=developer_user.id,
        project_id=test_project.id,
        role_id=developer_role.id
    ))
    
    db.add(ProjectRole(
        user_id=viewer_user.id,
        project_id=test_project.id,
        role_id=viewer_role.id
    ))
    
    db.commit()
    
    # Retourner les données de test
    return {
        "db": db,
        "admin_user": admin_user,
        "manager_user": manager_user,
        "developer_user": developer_user,
        "viewer_user": viewer_user,
        "super_admin_role": super_admin_role,
        "admin_role": admin_role,
        "project_owner_role": project_owner_role,
        "developer_role": developer_role,
        "viewer_role": viewer_role,
        "project_create_perm": project_create_perm,
        "project_read_perm": project_read_perm,
        "project_update_perm": project_update_perm,
        "project_delete_perm": project_delete_perm,
        "test_project": test_project
    }
    
def create_token(user: User) -> str:
    """Crée un token JWT pour un utilisateur"""
    return create_access_token(data={"sub": user.username})

def test_super_admin_permissions(client, test_data):
    """Test des permissions du super administrateur"""
    token = create_token(test_data["admin_user"])
    
    # Tester la création de projet
    response = client.post(
        "/projects/projects",
        json={"name": "Nouveau Projet", "description": "Description", "type": "software"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Tester la lecture de tous les projets
    response = client.get("/projects/projects", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Tester la modification de projet
    response = client.put(
        f"/projects/projects/{test_data['test_project'].id}",
        json={"name": "Projet Modifié"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Tester la suppression de projet
    response = client.delete(
        f"/projects/projects/{test_data['test_project'].id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_admin_permissions(client, test_data):
    """Test des permissions de l'administrateur"""
    token = create_token(test_data["manager_user"])
    
    # Tester la création de projet (autorisé)
    response = client.post(
        "/projects/projects",
        json={"name": "Projet Admin", "description": "Description", "type": "software"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Tester la lecture de projets (autorisé)
    response = client.get("/projects/projects", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Tester la modification de projet (autorisé)
    response = client.put(
        f"/projects/projects/{test_data['test_project'].id}",
        json={"name": "Projet Modifié par Admin"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Tester la suppression de projet (non autorisé pour admin)
    response = client.delete(
        f"/projects/projects/{test_data['test_project'].id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Forbidden

def test_developer_project_permissions(client, test_data):
    """Test des permissions du développeur sur un projet"""
    token = create_token(test_data["developer_user"])
    
    # Tester la lecture de projet (autorisé)
    response = client.get(
        f"/projects/projects/{test_data['test_project'].id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Tester la modification de projet (non autorisé)
    response = client.put(
        f"/projects/projects/{test_data['test_project'].id}",
        json={"name": "Projet Modifié par Dev"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    
    # Tester la création de projet (non autorisé)
    response = client.post(
        "/projects/projects",
        json={"name": "Nouveau Projet Dev", "description": "Description", "type": "software"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_viewer_project_permissions(client, test_data):
    """Test des permissions de l'observateur sur un projet"""
    token = create_token(test_data["viewer_user"])
    
    # Tester la lecture de projet (autorisé)
    response = client.get(
        f"/projects/projects/{test_data['test_project'].id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Tester la modification de projet (non autorisé)
    response = client.put(
        f"/projects/projects/{test_data['test_project'].id}",
        json={"name": "Projet Modifié par Viewer"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    
    # Tester la création de projet (non autorisé)
    response = client.post(
        "/projects/projects",
        json={"name": "Nouveau Projet Viewer", "description": "Description", "type": "software"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_unauthorized_access(client):
    """Test d'accès non autorisé sans token"""
    # Tester sans token
    response = client.get("/projects/projects")
    assert response.status_code == 401  # Unauthorized
    
    # Tester avec un token invalide
    response = client.get("/projects/projects", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_permission_system_functions(test_data):
    """Test des fonctions du système de permission"""
    from app.auth.permission_system import PermissionSystem
    
    permission_system = PermissionSystem(test_data["db"])
    
    # Tester has_permission pour super admin
    assert permission_system.has_permission(test_data["admin_user"], "project_create") == True
    assert permission_system.has_permission(test_data["admin_user"], "project_delete") == True
    
    # Tester has_permission pour admin
    assert permission_system.has_permission(test_data["manager_user"], "project_create") == True
    assert permission_system.has_permission(test_data["manager_user"], "project_delete") == False
    
    # Tester has_any_permission
    assert permission_system.has_any_permission(
        test_data["developer_user"],
        ["project_create", "project_read"],
        test_data["test_project"].id
    ) == True
    
    # Tester has_all_permissions
    assert permission_system.has_all_permissions(
        test_data["developer_user"],
        ["project_read"],
        test_data["test_project"].id
    ) == True
    
    assert permission_system.has_all_permissions(
        test_data["developer_user"],
        ["project_read", "project_update"],
        test_data["test_project"].id
    ) == False

def test_permission_decorators():
    """Test des décorateurs de permission"""
    from app.auth.permission_decorators import (
        permission_required, any_permission_required, all_permissions_required
    )
    
    # Tester que les décorateurs sont bien définis
    assert callable(permission_required)
    assert callable(any_permission_required)
    assert callable(all_permissions_required)

def test_middleware_authorization(client):
    """Test du middleware d'autorisation"""
    # Le middleware devrait bloquer les requêtes non authentifiées
    response = client.get("/projects/projects")
    assert response.status_code == 401
    
    # Le middleware devrait autoriser les endpoints publics
    response = client.get("/health")
    assert response.status_code == 200
    
    response = client.get("/docs")
    assert response.status_code == 200