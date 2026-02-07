"""
Modelo de Cliente - Gestión de clientes (tiendas, distribuidores, mayoristas)
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TipoCliente(str, enum.Enum):
    MINORISTA = "minorista"
    MAYORISTA = "mayorista"
    DISTRIBUIDOR = "distribuidor"
    CADENA = "cadena"  # Supermercados, farmacias en cadena
    INSTITUCIONAL = "institucional"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    
    # Datos de la empresa/negocio
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(200))
    ruc = Column(String(20), unique=True, index=True)
    
    # Tipo y categoría
    tipo = Column(SQLEnum(TipoCliente), default=TipoCliente.MINORISTA)
    
    # Contacto principal
    contacto_nombre = Column(String(100))
    contacto_telefono = Column(String(20))
    contacto_email = Column(String(100))
    
    # Dirección
    direccion = Column(String(300))
    distrito = Column(String(100))
    provincia = Column(String(100))
    departamento = Column(String(100))
    referencia = Column(Text)
    
    # Coordenadas para logística
    latitud = Column(Float)
    longitud = Column(Float)
    
    # Condiciones comerciales
    limite_credito = Column(Float, default=0.0)
    dias_credito = Column(Integer, default=0)  # 0 = contado
    descuento_especial = Column(Float, default=0.0)  # Porcentaje
    
    # Estado
    activo = Column(Boolean, default=True)
    verificado = Column(Boolean, default=False)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    ventas = relationship("Venta", back_populates="cliente")
    rutas = relationship("RutaCliente", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente {self.codigo} - {self.razon_social}>"
    
    @property
    def direccion_completa(self):
        partes = [self.direccion, self.distrito, self.provincia, self.departamento]
        return ", ".join(filter(None, partes))
