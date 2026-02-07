"""
Modelo de Proveedor - Gestión de proveedores y compras
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TipoProveedor(str, enum.Enum):
    FABRICANTE = "fabricante"
    DISTRIBUIDOR = "distribuidor"
    IMPORTADOR = "importador"


class EstadoCompra(str, enum.Enum):
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    EN_TRANSITO = "en_transito"
    RECIBIDA = "recibida"
    CANCELADA = "cancelada"


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    
    # Datos de la empresa
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(200))
    ruc = Column(String(20), unique=True, index=True)
    tipo = Column(SQLEnum(TipoProveedor), default=TipoProveedor.DISTRIBUIDOR)
    
    # Contacto
    contacto_nombre = Column(String(100))
    contacto_telefono = Column(String(20))
    contacto_email = Column(String(100))
    
    # Dirección
    direccion = Column(String(300))
    ciudad = Column(String(100))
    pais = Column(String(100), default="Perú")
    
    # Condiciones comerciales
    dias_entrega = Column(Integer, default=7)
    dias_credito = Column(Integer, default=30)
    descuento_pronto_pago = Column(Float, default=0.0)
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    compras = relationship("Compra", back_populates="proveedor")
    
    def __repr__(self):
        return f"<Proveedor {self.codigo} - {self.razon_social}>"


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, index=True, nullable=False)
    
    # Proveedor
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    
    # Fechas
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    fecha_entrega_esperada = Column(DateTime)
    fecha_recepcion = Column(DateTime)
    
    # Estado
    estado = Column(SQLEnum(EstadoCompra), default=EstadoCompra.PENDIENTE)
    
    # Totales
    subtotal = Column(Float, default=0.0)
    impuesto = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Documento del proveedor
    factura_proveedor = Column(String(50))
    
    # Observaciones
    observaciones = Column(Text)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    proveedor = relationship("Proveedor", back_populates="compras")
    detalles = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Compra {self.numero} - {self.estado}>"


class DetalleCompra(Base):
    __tablename__ = "detalles_compra"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    
    # Para control de recepción
    cantidad_recibida = Column(Integer, default=0)
    
    # Relaciones
    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_compra")
    
    def __repr__(self):
        return f"<DetalleCompra {self.compra_id} - {self.producto_id}>"
