"""
Schemas de Inventario
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.inventario import TipoAlmacen, TipoMovimiento


# ============ ALMACÉN ============
class AlmacenBase(BaseModel):
    codigo: str
    nombre: str
    tipo: TipoAlmacen = TipoAlmacen.PRINCIPAL
    direccion: Optional[str] = None
    distrito: Optional[str] = None
    ciudad: Optional[str] = None
    responsable: Optional[str] = None
    telefono: Optional[str] = None


class AlmacenCreate(AlmacenBase):
    pass


class AlmacenUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[TipoAlmacen] = None
    direccion: Optional[str] = None
    distrito: Optional[str] = None
    ciudad: Optional[str] = None
    responsable: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None


class AlmacenResponse(AlmacenBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ INVENTARIO ============
class InventarioBase(BaseModel):
    producto_id: int
    almacen_id: int
    stock_actual: int = 0
    ubicacion: Optional[str] = None
    lote: Optional[str] = None
    fecha_vencimiento: Optional[datetime] = None


class InventarioCreate(InventarioBase):
    pass


class InventarioUpdate(BaseModel):
    stock_actual: Optional[int] = None
    stock_reservado: Optional[int] = None
    ubicacion: Optional[str] = None
    lote: Optional[str] = None
    fecha_vencimiento: Optional[datetime] = None


class InventarioResponse(InventarioBase):
    id: int
    stock_reservado: int
    stock_disponible: int
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


class InventarioConProducto(InventarioResponse):
    producto_nombre: str
    producto_codigo: str
    almacen_nombre: str


# ============ MOVIMIENTO ============
class MovimientoBase(BaseModel):
    almacen_id: int
    producto_id: int
    tipo: TipoMovimiento
    cantidad: int
    motivo: Optional[str] = None


class MovimientoCreate(MovimientoBase):
    documento_tipo: Optional[str] = None
    documento_id: Optional[int] = None
    documento_numero: Optional[str] = None


class MovimientoResponse(MovimientoBase):
    id: int
    stock_anterior: int
    stock_posterior: int
    documento_tipo: Optional[str] = None
    documento_numero: Optional[str] = None
    fecha: datetime

    class Config:
        from_attributes = True


# ============ AJUSTE DE INVENTARIO ============
class AjusteInventario(BaseModel):
    almacen_id: int
    producto_id: int
    cantidad: int  # Positivo para agregar, negativo para restar
    motivo: str


# ============ TRANSFERENCIA ============
class TransferenciaInventario(BaseModel):
    almacen_origen_id: int
    almacen_destino_id: int
    producto_id: int
    cantidad: int
    motivo: Optional[str] = None
