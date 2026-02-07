"""
Schemas de Logística
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, time
from app.models.logistica import EstadoEnvio, TipoVehiculo


# ============ VEHÍCULO ============
class VehiculoBase(BaseModel):
    codigo: str
    placa: str
    tipo: TipoVehiculo = TipoVehiculo.FURGONETA
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    capacidad_peso: Optional[float] = None
    capacidad_volumen: Optional[float] = None


class VehiculoCreate(VehiculoBase):
    soat_vencimiento: Optional[datetime] = None
    revision_tecnica_vencimiento: Optional[datetime] = None


class VehiculoUpdate(BaseModel):
    placa: Optional[str] = None
    tipo: Optional[TipoVehiculo] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    capacidad_peso: Optional[float] = None
    capacidad_volumen: Optional[float] = None
    activo: Optional[bool] = None
    disponible: Optional[bool] = None
    soat_vencimiento: Optional[datetime] = None
    revision_tecnica_vencimiento: Optional[datetime] = None


class VehiculoResponse(VehiculoBase):
    id: int
    activo: bool
    disponible: bool
    soat_vencimiento: Optional[datetime] = None
    revision_tecnica_vencimiento: Optional[datetime] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ CONDUCTOR ============
class ConductorBase(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    dni: str
    telefono: Optional[str] = None
    licencia_numero: Optional[str] = None
    licencia_categoria: Optional[str] = None


class ConductorCreate(ConductorBase):
    licencia_vencimiento: Optional[datetime] = None


class ConductorUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    licencia_numero: Optional[str] = None
    licencia_categoria: Optional[str] = None
    licencia_vencimiento: Optional[datetime] = None
    activo: Optional[bool] = None
    disponible: Optional[bool] = None


class ConductorResponse(ConductorBase):
    id: int
    activo: bool
    disponible: bool
    licencia_vencimiento: Optional[datetime] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ ZONA REPARTO ============
class ZonaRepartoBase(BaseModel):
    codigo: str
    nombre: str
    distritos: Optional[str] = None
    descripcion: Optional[str] = None
    dias_reparto: Optional[str] = None


class ZonaRepartoCreate(ZonaRepartoBase):
    pass


class ZonaRepartoUpdate(BaseModel):
    nombre: Optional[str] = None
    distritos: Optional[str] = None
    descripcion: Optional[str] = None
    dias_reparto: Optional[str] = None
    activo: Optional[bool] = None


class ZonaRepartoResponse(ZonaRepartoBase):
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ ENVÍO ============
class EnvioBase(BaseModel):
    venta_id: int
    fecha_programada: Optional[datetime] = None
    observaciones: Optional[str] = None


class EnvioCreate(EnvioBase):
    ruta_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None


class EnvioUpdate(BaseModel):
    ruta_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None
    orden_entrega: Optional[int] = None
    estado: Optional[EstadoEnvio] = None
    fecha_programada: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    firma_recibido: Optional[bool] = None
    nombre_recibio: Optional[str] = None
    dni_recibio: Optional[str] = None
    observaciones: Optional[str] = None
    motivo_no_entrega: Optional[str] = None
    latitud_entrega: Optional[float] = None
    longitud_entrega: Optional[float] = None


class EnvioResponse(EnvioBase):
    id: int
    codigo: str
    estado: EstadoEnvio
    ruta_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None
    orden_entrega: Optional[int] = None
    fecha_entrega: Optional[datetime] = None
    firma_recibido: bool
    nombre_recibio: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ RUTA REPARTO ============
class RutaRepartoBase(BaseModel):
    codigo: str
    nombre: str
    fecha: datetime
    zona_id: Optional[int] = None


class RutaRepartoCreate(RutaRepartoBase):
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None
    envio_ids: List[int] = []


class RutaRepartoUpdate(BaseModel):
    nombre: Optional[str] = None
    fecha: Optional[datetime] = None
    zona_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None
    completada: Optional[bool] = None
    kilometros_recorridos: Optional[float] = None


class RutaRepartoResponse(RutaRepartoBase):
    id: int
    vehiculo_id: Optional[int] = None
    conductor_id: Optional[int] = None
    total_entregas: int
    entregas_exitosas: int
    entregas_fallidas: int
    kilometros_recorridos: float
    completada: bool
    fecha_creacion: datetime
    envios: List[EnvioResponse] = []

    class Config:
        from_attributes = True
