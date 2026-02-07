"""
Schemas de Cliente
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.cliente import TipoCliente


class ClienteBase(BaseModel):
    codigo: str
    razon_social: str
    nombre_comercial: Optional[str] = None
    ruc: Optional[str] = None
    tipo: TipoCliente = TipoCliente.MINORISTA
    
    # Contacto
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None
    
    # Dirección
    direccion: Optional[str] = None
    distrito: Optional[str] = None
    provincia: Optional[str] = None
    departamento: Optional[str] = None
    referencia: Optional[str] = None
    
    # Coordenadas
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    
    # Condiciones comerciales
    limite_credito: float = 0.0
    dias_credito: int = 0
    descuento_especial: float = 0.0


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    nombre_comercial: Optional[str] = None
    ruc: Optional[str] = None
    tipo: Optional[TipoCliente] = None
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[str] = None
    direccion: Optional[str] = None
    distrito: Optional[str] = None
    provincia: Optional[str] = None
    departamento: Optional[str] = None
    referencia: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    limite_credito: Optional[float] = None
    dias_credito: Optional[int] = None
    descuento_especial: Optional[float] = None
    activo: Optional[bool] = None
    verificado: Optional[bool] = None


class ClienteResponse(ClienteBase):
    id: int
    activo: bool
    verificado: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ClienteListResponse(BaseModel):
    total: int
    items: List[ClienteResponse]
