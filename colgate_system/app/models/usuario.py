"""
Modelo de Usuario - Gestión de acceso y roles
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    GERENTE = "gerente"
    VENDEDOR = "vendedor"
    ALMACENERO = "almacenero"
    LOGISTICA = "logistica"
    CONTADOR = "contador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Información personal
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True)
    telefono = Column(String(20))
    
    # Rol y estado
    rol = Column(SQLEnum(RolUsuario), default=RolUsuario.VENDEDOR)
    activo = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acceso = Column(DateTime)
    
    # Relaciones
    ventas = relationship("Venta", back_populates="vendedor")
    
    def __repr__(self):
        return f"<Usuario {self.username} - {self.rol}>"
