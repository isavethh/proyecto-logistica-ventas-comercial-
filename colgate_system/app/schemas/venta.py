"""
Schemas de Venta
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.venta import EstadoVenta, TipoPago, TipoDocumento


# ============ DETALLE VENTA ============
class DetalleVentaBase(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    descuento_porcentaje: float = 0.0
    descuento_monto: float = 0.0


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVentaResponse(DetalleVentaBase):
    id: int
    cantidad_entregada: int
    subtotal: float

    class Config:
        from_attributes = True


class DetalleVentaConProducto(DetalleVentaResponse):
    producto_nombre: str
    producto_codigo: str


# ============ VENTA ============
class VentaBase(BaseModel):
    cliente_id: int
    tipo_documento: TipoDocumento = TipoDocumento.FACTURA
    tipo_pago: TipoPago = TipoPago.CONTADO
    fecha_entrega_solicitada: Optional[datetime] = None
    direccion_entrega: Optional[str] = None
    referencia_entrega: Optional[str] = None
    observaciones: Optional[str] = None


class VentaCreate(VentaBase):
    detalles: List[DetalleVentaCreate]


class VentaUpdate(BaseModel):
    estado: Optional[EstadoVenta] = None
    tipo_documento: Optional[TipoDocumento] = None
    numero_documento: Optional[str] = None
    tipo_pago: Optional[TipoPago] = None
    fecha_entrega_solicitada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None
    fecha_vencimiento_pago: Optional[datetime] = None
    descuento: Optional[float] = None
    direccion_entrega: Optional[str] = None
    referencia_entrega: Optional[str] = None
    observaciones: Optional[str] = None


class VentaResponse(VentaBase):
    id: int
    numero: str
    estado: EstadoVenta
    numero_documento: Optional[str] = None
    fecha_pedido: datetime
    fecha_entrega_real: Optional[datetime] = None
    fecha_vencimiento_pago: Optional[datetime] = None
    subtotal: float
    descuento: float
    impuesto: float
    total: float
    vendedor_id: Optional[int] = None
    detalles: List[DetalleVentaResponse] = []

    class Config:
        from_attributes = True


class VentaListResponse(BaseModel):
    total: int
    items: List[VentaResponse]


# ============ PAGO ============
class PagoVentaBase(BaseModel):
    venta_id: int
    monto: float
    tipo_pago: TipoPago
    referencia: Optional[str] = None


class PagoVentaCreate(PagoVentaBase):
    pass


class PagoVentaResponse(PagoVentaBase):
    id: int
    confirmado: bool
    fecha: datetime

    class Config:
        from_attributes = True
