"""
Modelo de Categoría - Clasificación de productos
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria")
    
    def __repr__(self):
        return f"<Categoria {self.codigo} - {self.nombre}>"


class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    pais_origen = Column(String(50))
    activo = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    productos = relationship("Producto", back_populates="marca")
    
    def __repr__(self):
        return f"<Marca {self.codigo} - {self.nombre}>"
