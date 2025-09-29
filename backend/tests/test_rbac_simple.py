# tests/test_rbac_simple.py
"""
Tests simplifiés du système RBAC
Vérifie le bon fonctionnement des permissions, rôles et autorisations sans dépendre du client HTTP
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.user import User
from app.models.role import Role, Permission, UserRole, ProjectRole
from app.models.project import Project
from app.auth.permission_system import PermissionSystem


# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_simple.db"


@pytest.fixture
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
    
    return TestingSessionLocal()


@pytest.fixture
def test_data(test_db):
    """Fixture pour les données de test"""
    db = test_db
    
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


def test_permission_system_functions(test_data):
    """Test des fonctions du système de permission"""
    permission_system = PermissionSystem(test_data["db"])
    
    # Tester has_permission pour super admin (permissions système)
    assert permission_system.has_permission(test_data["admin_user"], "project_create") == True
    assert permission_system.has_permission(test_data["admin_user"], "project_read_all") == True
    assert permission_system.has_permission(test_data["admin_user"], "project_manage_all") == True
    
    # Tester has_permission pour admin
    assert permission_system.has_permission(test_data["manager_user"], "project_create") == True
    assert permission_system.has_permission(test_data["manager_user"], "project_manage_all") == True
    assert permission_system.has_permission(test_data["manager_user"], "system_config") == False
    
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


def test_role_permission_assignment(test_data):
    """Test de l'assignation des permissions aux rôles"""
    # Vérifier que le super admin a toutes les permissions
    super_admin_perms = [perm.name for perm in test_data["super_admin_role"].permissions]
    assert "project_create" in super_admin_perms
    assert "project_read" in super_admin_perms
    assert "project_update" in super_admin_perms
    assert "project_delete" in super_admin_perms
    
    # Vérifier que l'admin n'a pas la permission de suppression
    admin_perms = [perm.name for perm in test_data["admin_role"].permissions]
    assert "project_create" in admin_perms
    assert "project_read" in admin_perms
    assert "project_update" in admin_perms
    assert "project_delete" not in admin_perms
    
    # Vérifier que le développeur a seulement la lecture
    developer_perms = [perm.name for perm in test_data["developer_role"].permissions]
    assert "project_read" in developer_perms
    assert "project_create" not in developer_perms
    assert "project_update" not in developer_perms
    assert "project_delete" not in developer_perms


def test_user_role_assignment(test_data):
    """Test de l'assignation des rôles aux utilisateurs"""
    # Vérifier que l'admin user a le rôle super_admin
    admin_roles = [ur.role.name for ur in test_data["admin_user"].user_roles]
    assert "super_admin" in admin_roles
    
    # Vérifier que le manager user a le rôle admin
    manager_roles = [ur.role.name for ur in test_data["manager_user"].user_roles]
    assert "admin" in manager_roles
    
    # Vérifier que le developer user a un rôle projet
    developer_project_roles = [pr.role.name for pr in test_data["developer_user"].project_roles]
    assert "developer" in developer_project_roles
    
    # Vérifier que le viewer user a un rôle projet
    viewer_project_roles = [pr.role.name for pr in test_data["viewer_user"].project_roles]
    assert "viewer" in viewer_project_roles


def test_permission_validation(test_data):
    """Test de la validation des permissions"""
    permission_system = PermissionSystem(test_data["db"])
    
    # Test des permissions globales (sans projet spécifique)
    assert permission_system.has_permission(test_data["admin_user"], "project_create") == True
    assert permission_system.has_permission(test_data["manager_user"], "project_create") == True
    assert permission_system.has_permission(test_data["developer_user"], "project_create") == False
    assert permission_system.has_permission(test_data["viewer_user"], "project_create") == False
    
    # Test des permissions spécifiques au projet
    assert permission_system.has_permission(
        test_data["developer_user"], 
        "project_read", 
        test_data["test_project"].id
    ) == True
    
    assert permission_system.has_permission(
        test_data["viewer_user"], 
        "project_read", 
        test_data["test_project"].id
    ) == True
    
    assert permission_system.has_permission(
        test_data["developer_user"], 
        "project_update", 
        test_data["test_project"].id
    ) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])