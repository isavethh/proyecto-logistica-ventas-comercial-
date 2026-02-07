"""
Modelo de Venta - Gestión de pedidos y facturación
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class EstadoVenta(str, enum.Enum):
    BORRADOR = "borrador"
    CONFIRMADO = "confirmado"
    EN_PREPARACION = "en_preparacion"
    LISTO_ENVIO = "listo_envio"
    EN_RUTA = "en_ruta"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class TipoPago(str, enum.Enum):
    CONTADO = "contado"
    CREDITO = "credito"
    TRANSFERENCIA = "transferencia"
    CHEQUE = "cheque"


class TipoDocumento(str, enum.Enum):
    FACTURA = "factura"
    BOLETA = "boleta"
    NOTA_VENTA = "nota_venta"


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, index=True, nullable=False)
    
    # Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Vendedor
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Fechas
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    fecha_entrega_solicitada = Column(DateTime)
    fecha_entrega_real = Column(DateTime)
    
    # Estado
    estado = Column(SQLEnum(EstadoVenta), default=EstadoVenta.BORRADOR)
    
    # Documento
    tipo_documento = Column(SQLEnum(TipoDocumento), default=TipoDocumento.FACTURA)
    numero_documento = Column(String(20))
    
    # Pago
    tipo_pago = Column(SQLEnum(TipoPago), default=TipoPago.CONTADO)
    fecha_vencimiento_pago = Column(DateTime)
    
    # Totales
    subtotal = Column(Float, default=0.0)
    descuento = Column(Float, default=0.0)
    impuesto = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Dirección de entrega (puede ser diferente a la del cliente)
    direccion_entrega = Column(String(300))
    referencia_entrega = Column(Text)
    
    # Observaciones
    observaciones = Column(Text)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="ventas")
    vendedor = relationship("Usuario", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    envio = relationship("Envio", back_populates="venta", uselist=False)
    
    def __repr__(self):
        return f"<Venta {self.numero} - {self.estado}>"
    
    def calcular_totales(self):
        self.subtotal = sum(d.subtotal for d in self.detalles)
        self.impuesto = self.subtotal * 0.18  # IGV 18%
        self.total = self.subtotal + self.impuesto - self.descuento


class DetalleVenta(Base):
    __tablename__ = "detalles_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    # Cantidades
    cantidad = Column(Integer, nullable=False)
    cantidad_entregada = Column(Integer, default=0)
    
    # Precios
    precio_unitario = Column(Float, nullable=False)
    descuento_porcentaje = Column(Float, default=0.0)
    descuento_monto = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    
    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")
    
    def __repr__(self):
        return f"<DetalleVenta {self.venta_id} - {self.producto_id}>"
    
    def calcular_subtotal(self):
        precio_con_descuento = self.precio_unitario * (1 - self.descuento_porcentaje / 100)
        self.subtotal = (precio_con_descuento * self.cantidad) - self.descuento_monto


class PagoVenta(Base):
    __tablename__ = "pagos_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    
    # Pago
    monto = Column(Float, nullable=False)
    tipo_pago = Column(SQLEnum(TipoPago), nullable=False)
    referencia = Column(String(100))  # Número de transferencia, cheque, etc.
    
    # Estado
    confirmado = Column(Boolean, default=False)
    
    # Auditoría
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    
    def __repr__(self):
        return f"<PagoVenta {self.venta_id} - {self.monto}>"
