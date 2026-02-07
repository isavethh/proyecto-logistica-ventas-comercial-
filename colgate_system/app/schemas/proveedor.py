"""
Schemas de Proveedor y Compras
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.proveedor import TipoProveedor, EstadoCompra


# ============ PROVEEDOR ============
class ProveedorBase(BaseModel):
    codigo: str
    razon_social: str
    nombre_comercial: Optional[str] = None
    ruc: Optional[str] = None
    tipo: TipoProveedor = TipoProveedor.DISTRIBUIDOR
    
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None
    
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: str = "Perú"
    
    dias_entrega: int = 7
    dias_credito: int = 30
    descuento_pronto_pago: float = 0.0


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_comercial: Optional[str] = None
    ruc: Optional[str] = None
    tipo: Optional[TipoProveedor] = None
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    dias_entrega: Optional[int] = None
    dias_credito: Optional[int] = None
    descuento_pronto_pago: Optional[float] = None
    activo: Optional[bool] = None


class ProveedorResponse(ProveedorBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ COMPRA ============
class DetalleCompraBase(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    descuento: float = 0.0


class DetalleCompraCreate(DetalleCompraBase):
    pass


class DetalleCompraResponse(DetalleCompraBase):
    id: int
    subtotal: float
    cantidad_recibida: int

    class Config:
        from_attributes = True


class CompraBase(BaseModel):
    proveedor_id: int
    fecha_entrega_esperada: Optional[datetime] = None
    observaciones: Optional[str] = None


class CompraCreate(CompraBase):
    detalles: List[DetalleCompraCreate]


class CompraUpdate(BaseModel):
    estado: Optional[EstadoCompra] = None
    fecha_entrega_esperada: Optional[datetime] = None
    fecha_recepcion: Optional[datetime] = None
    factura_proveedor: Optional[str] = None
    observaciones: Optional[str] = None


class CompraResponse(CompraBase):
    id: int
    numero: str
    estado: EstadoCompra
    fecha_pedido: datetime
    fecha_recepcion: Optional[datetime] = None
    subtotal: float
    impuesto: float
    total: float
    factura_proveedor: Optional[str] = None
    detalles: List[DetalleCompraResponse] = []

    class Config:
        from_attributes = True
