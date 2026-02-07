"""
Modelo de Inventario - Control de stock por almacén
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TipoAlmacen(str, enum.Enum):
    PRINCIPAL = "principal"
    SECUNDARIO = "secundario"
    TRANSITO = "transito"
    DEVOLUCION = "devolucion"


class TipoMovimiento(str, enum.Enum):
    ENTRADA_COMPRA = "entrada_compra"
    ENTRADA_DEVOLUCION = "entrada_devolucion"
    ENTRADA_AJUSTE = "entrada_ajuste"
    ENTRADA_TRANSFERENCIA = "entrada_transferencia"
    SALIDA_VENTA = "salida_venta"
    SALIDA_DEVOLUCION = "salida_devolucion"
    SALIDA_AJUSTE = "salida_ajuste"
    SALIDA_TRANSFERENCIA = "salida_transferencia"
    SALIDA_MERMA = "salida_merma"


class Almacen(Base):
    __tablename__ = "almacenes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo = Column(SQLEnum(TipoAlmacen), default=TipoAlmacen.PRINCIPAL)
    
    # Ubicación
    direccion = Column(String(300))
    distrito = Column(String(100))
    ciudad = Column(String(100))
    
    # Contacto
    responsable = Column(String(100))
    telefono = Column(String(20))
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    inventarios = relationship("Inventario", back_populates="almacen")
    movimientos = relationship("MovimientoInventario", back_populates="almacen")
    
    def __repr__(self):
        return f"<Almacen {self.codigo} - {self.nombre}>"


class Inventario(Base):
    __tablename__ = "inventarios"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    almacen_id = Column(Integer, ForeignKey("almacenes.id"), nullable=False)
    
    # Stock
    stock_actual = Column(Integer, default=0)
    stock_reservado = Column(Integer, default=0)  # Reservado para pedidos pendientes
    stock_disponible = Column(Integer, default=0)  # stock_actual - stock_reservado
    
    # Ubicación en almacén
    ubicacion = Column(String(50))  # Ej: "A-01-03" (Pasillo A, Estante 1, Nivel 3)
    
    # Lote y vencimiento (importante para productos perecibles)
    lote = Column(String(50))
    fecha_vencimiento = Column(DateTime)
    
    # Auditoría
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    producto = relationship("Producto", back_populates="inventarios")
    almacen = relationship("Almacen", back_populates="inventarios")
    
    def __repr__(self):
        return f"<Inventario {self.producto_id} en {self.almacen_id}: {self.stock_actual}>"
    
    def actualizar_disponible(self):
        self.stock_disponible = self.stock_actual - self.stock_reservado


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    almacen_id = Column(Integer, ForeignKey("almacenes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # Tipo y cantidad
    tipo = Column(SQLEnum(TipoMovimiento), nullable=False)
    cantidad = Column(Integer, nullable=False)
    
    # Stock resultante
    stock_anterior = Column(Integer, nullable=False)
    stock_posterior = Column(Integer, nullable=False)
    
    # Referencia al documento origen
    documento_tipo = Column(String(50))  # venta, compra, transferencia, ajuste
    documento_id = Column(Integer)
    documento_numero = Column(String(50))
    
    # Información adicional
    motivo = Column(Text)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Auditoría
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    almacen = relationship("Almacen", back_populates="movimientos")
    
    def __repr__(self):
        return f"<Movimiento {self.tipo} - {self.cantidad}>"
