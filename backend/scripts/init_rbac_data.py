# scripts/init_rbac_data.py
"""
Script de migration des données pour initialiser le système RBAC
Crée les rôles système et les permissions dans la base de données
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Ajouter le chemin du projet pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import Base, get_db
from app.models.role import Role, Permission, UserRole, ProjectRole
from app.models.user import User
from app.models.project import Project
from app.auth.permission_matrix import (
    ROLES_SYSTEM, 
    ROLES_PROJECT, 
    PERMISSIONS,
    ROLE_SYSTEM_PERMISSIONS,
    ROLE_PROJECT_PERMISSIONS
)


class RBACDataMigration:
    """Classe pour gérer la migration des données RBAC"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def init_system_roles(self):
        """Initialise les rôles système"""
        print("Initialisation des rôles système...")
        
        for role_name, description, is_system in ROLES_SYSTEM:
            # Vérifier si le rôle existe déjà
            existing_role = self.db.query(Role).filter(Role.name == role_name).first()
            
            if not existing_role:
                role = Role(
                    name=role_name,
                    description=description,
                    is_system_role=is_system
                )
                self.db.add(role)
                print(f"✓ Rôle système créé: {role_name}")
            else:
                print(f"→ Rôle système existant: {role_name}")
        
        self.db.commit()
    
    def init_project_roles(self):
        """Initialise les rôles projet"""
        print("Initialisation des rôles projet...")
        
        for role_name, description in ROLES_PROJECT:
            # Vérifier si le rôle existe déjà
            existing_role = self.db.query(Role).filter(Role.name == role_name).first()
            
            if not existing_role:
                role = Role(
                    name=role_name,
                    description=description,
                    is_system_role=False
                )
                self.db.add(role)
                print(f"✓ Rôle projet créé: {role_name}")
            else:
                print(f"→ Rôle projet existant: {role_name}")
        
        self.db.commit()
    
    def init_permissions(self):
        """Initialise les permissions"""
        print("Initialisation des permissions...")
        
        for perm_name, resource, action, description in PERMISSIONS:
            # Vérifier si la permission existe déjà
            existing_perm = self.db.query(Permission).filter(Permission.name == perm_name).first()
            
            if not existing_perm:
                permission = Permission(
                    name=perm_name,
                    resource=resource,
                    action=action,
                    description=description
                )
                self.db.add(permission)
                print(f"✓ Permission créée: {perm_name} ({resource}:{action})")
            else:
                print(f"→ Permission existante: {perm_name}")
        
        self.db.commit()
    
    def assign_system_role_permissions(self):
        """Assigne les permissions aux rôles système"""
        print("Assignation des permissions aux rôles système...")
        
        for role_name, permissions in ROLE_SYSTEM_PERMISSIONS.items():
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                print(f"⚠ Rôle système non trouvé: {role_name}")
                continue
            
            # Récupérer les permissions actuelles du rôle
            current_permissions = {perm.name for perm in role.permissions}
            
            for perm_name in permissions:
                permission = self.db.query(Permission).filter(Permission.name == perm_name).first()
                if permission and perm_name not in current_permissions:
                    role.permissions.append(permission)
                    print(f"✓ Permission {perm_name} assignée au rôle {role_name}")
            
            self.db.commit()
    
    def assign_project_role_permissions(self):
        """Assigne les permissions aux rôles projet"""
        print("Assignation des permissions aux rôles projet...")
        
        for role_name, permissions in ROLE_PROJECT_PERMISSIONS.items():
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                print(f"⚠ Rôle projet non trouvé: {role_name}")
                continue
            
            # Récupérer les permissions actuelles du rôle
            current_permissions = {perm.name for perm in role.permissions}
            
            for perm_name in permissions:
                permission = self.db.query(Permission).filter(Permission.name == perm_name).first()
                if permission and perm_name not in current_permissions:
                    role.permissions.append(permission)
                    print(f"✓ Permission {perm_name} assignée au rôle {role_name}")
            
            self.db.commit()
    
    def create_default_admin_user(self):
        """Crée un utilisateur administrateur par défaut si nécessaire"""
        print("Vérification de l'utilisateur administrateur...")
        
        # Vérifier s'il existe déjà un super administrateur
        admin_role = self.db.query(Role).filter(Role.name == "super_admin").first()
        if not admin_role:
            print("⚠ Rôle super_admin non trouvé")
            return
        
        # Vérifier s'il y a déjà des utilisateurs avec ce rôle
        existing_admin = self.db.query(UserRole).filter(UserRole.role_id == admin_role.id).first()
        if existing_admin:
            print("→ Utilisateur administrateur existe déjà")
            return
        
        # Créer un utilisateur administrateur par défaut
        # Note: Dans un environnement de production, cela devrait être configuré via des variables d'environnement
        admin_user = self.db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("⚠ Aucun utilisateur 'admin' trouvé. Veuillez créer manuellement un utilisateur administrateur.")
            return
        
        # Assigner le rôle super_admin à l'utilisateur admin
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        self.db.add(user_role)
        self.db.commit()
        print("✓ Rôle super_admin assigné à l'utilisateur admin")
    
    def migrate_existing_contributors(self):
        """Migre les contributeurs existants vers le nouveau système RBAC"""
        print("Migration des contributeurs existants...")
        
        # Récupérer le rôle "developer" par défaut pour les contributeurs existants
        developer_role = self.db.query(Role).filter(Role.name == "developer").first()
        if not developer_role:
            print("⚠ Rôle developer non trouvé")
            return
        
        # Pour chaque projet, assigner le rôle developer aux contributeurs existants
        projects = self.db.query(Project).all()
        for project in projects:
            # Récupérer les contributeurs du projet (via la table contributors existante)
            # Note: Cette partie dépend de votre modèle de données existant
            # Vous devrez peut-être adapter cette logique en fonction de votre implémentation
            
            print(f"→ Migration des contributeurs pour le projet {project.name} (ID: {project.id})")
            
            # Exemple de logique de migration (à adapter)
            # for contributor in project.contributors:
            #     project_role = ProjectRole(
            #         user_id=contributor.user_id,
            #         project_id=project.id,
            #         role_id=developer_role.id
            #     )
            #     self.db.add(project_role)
        
        self.db.commit()
        print("✓ Migration des contributeurs terminée")
    
    def run_migration(self):
        """Exécute la migration complète"""
        print("🚀 Début de la migration des données RBAC...")
        
        try:
            self.init_system_roles()
            self.init_project_roles()
            self.init_permissions()
            self.assign_system_role_permissions()
            self.assign_project_role_permissions()
            self.create_default_admin_user()
            self.migrate_existing_contributors()
            
            print("✅ Migration RBAC terminée avec succès!")
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erreur lors de la migration: {str(e)}")
            raise


def main():
    """Fonction principale"""
    try:
        # Obtenir la session de base de données
        db = next(get_db())
        
        # Créer et exécuter la migration
        migration = RBACDataMigration(db)
        migration.run_migration()
        
    except SQLAlchemyError as e:
        print(f"❌ Erreur de base de données: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()