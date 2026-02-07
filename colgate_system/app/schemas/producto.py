"""
Schemas de Producto y Categoría
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.producto import UnidadMedida


# ============ CATEGORÍA ============
class CategoriaBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CategoriaResponse(CategoriaBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ MARCA ============
class MarcaBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    pais_origen: Optional[str] = None


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    pais_origen: Optional[str] = None
    activo: Optional[bool] = None


class MarcaResponse(MarcaBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ PRODUCTO ============
class ProductoBase(BaseModel):
    codigo: str
    codigo_barras: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None
    presentacion: Optional[str] = None
    contenido: Optional[str] = None
    unidad_medida: UnidadMedida = UnidadMedida.UNIDAD
    precio_compra: float = 0.0
    precio_venta: float = 0.0
    precio_mayorista: float = 0.0
    stock_minimo: int = 10
    stock_maximo: int = 1000


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo_barras: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None
    presentacion: Optional[str] = None
    contenido: Optional[str] = None
    unidad_medida: Optional[UnidadMedida] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    precio_mayorista: Optional[float] = None
    stock_minimo: Optional[int] = None
    stock_maximo: Optional[int] = None
    activo: Optional[bool] = None
    destacado: Optional[bool] = None


class ProductoResponse(ProductoBase):
    id: int
    activo: bool
    destacado: bool
    fecha_creacion: datetime
    categoria: Optional[CategoriaResponse] = None
    marca: Optional[MarcaResponse] = None

    class Config:
        from_attributes = True


class ProductoListResponse(BaseModel):
    total: int
    items: List[ProductoResponse]
