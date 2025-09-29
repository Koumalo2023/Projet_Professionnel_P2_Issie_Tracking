# app/models/role.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from app.database.database import Base

# Table d'association pour les permissions des rôles
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Role(Base):
    """Modèle pour les rôles système et projet"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_system_role = Column(Boolean, default=False)
    
    # Relations
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role")
    project_roles = relationship("ProjectRole", back_populates="role")

class Permission(Base):
    """Modèle pour les permissions granulaires"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    resource = Column(String(50), nullable=False)  # 'project', 'issue', 'comment', etc.
    action = Column(String(50), nullable=False)    # 'create', 'read', 'update', 'delete'
    description = Column(String(255))
    
    # Relations
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class UserRole(Base):
    """Association des rôles système aux utilisateurs"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

class ProjectRole(Base):
    """Association des rôles projet aux utilisateurs"""
    __tablename__ = "project_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="project_roles")
    project = relationship("Project", back_populates="project_roles")
    role = relationship("Role", back_populates="project_roles")