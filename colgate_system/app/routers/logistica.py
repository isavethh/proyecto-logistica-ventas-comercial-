"""
Router de Logística
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from app.database import get_db
from app.models.usuario import Usuario
from app.models.logistica import EstadoEnvio
from app.schemas.logistica import (
    VehiculoCreate, VehiculoUpdate, VehiculoResponse,
    ConductorCreate, ConductorUpdate, ConductorResponse,
    ZonaRepartoCreate, ZonaRepartoUpdate, ZonaRepartoResponse,
    EnvioCreate, EnvioUpdate, EnvioResponse,
    RutaRepartoCreate, RutaRepartoUpdate, RutaRepartoResponse
)
from app.services import logistica_service
from app.services.auth import get_usuario_actual, es_logistica

router = APIRouter(prefix="/logistica", tags=["Logística"])


# ============ DASHBOARD ============
@router.get("/dashboard")
async def dashboard_logistica(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Dashboard de logística con métricas del día"""
    return logistica_service.get_dashboard_logistica(db)


# ============ VEHÍCULOS ============
@router.get("/vehiculos", response_model=list[VehiculoResponse])
async def listar_vehiculos(
    solo_activos: bool = True,
    solo_disponibles: bool = False,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar vehículos"""
    return logistica_service.get_vehiculos(db, solo_activos, solo_disponibles)


@router.get("/vehiculos/{vehiculo_id}", response_model=VehiculoResponse)
async def obtener_vehiculo(
    vehiculo_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener vehículo por ID"""
    vehiculo = logistica_service.get_vehiculo(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


@router.post("/vehiculos", response_model=VehiculoResponse)
async def crear_vehiculo(
    vehiculo: VehiculoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Crear nuevo vehículo"""
    return logistica_service.crear_vehiculo(db, vehiculo)


@router.put("/vehiculos/{vehiculo_id}", response_model=VehiculoResponse)
async def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo: VehiculoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Actualizar vehículo"""
    resultado = logistica_service.actualizar_vehiculo(db, vehiculo_id, vehiculo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return resultado


# ============ CONDUCTORES ============
@router.get("/conductores", response_model=list[ConductorResponse])
async def listar_conductores(
    solo_activos: bool = True,
    solo_disponibles: bool = False,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar conductores"""
    return logistica_service.get_conductores(db, solo_activos, solo_disponibles)


@router.get("/conductores/{conductor_id}", response_model=ConductorResponse)
async def obtener_conductor(
    conductor_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener conductor por ID"""
    conductor = logistica_service.get_conductor(db, conductor_id)
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return conductor


@router.post("/conductores", response_model=ConductorResponse)
async def crear_conductor(
    conductor: ConductorCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Crear nuevo conductor"""
    return logistica_service.crear_conductor(db, conductor)


@router.put("/conductores/{conductor_id}", response_model=ConductorResponse)
async def actualizar_conductor(
    conductor_id: int,
    conductor: ConductorUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Actualizar conductor"""
    resultado = logistica_service.actualizar_conductor(db, conductor_id, conductor)
    if not resultado:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")
    return resultado


# ============ ZONAS ============
@router.get("/zonas", response_model=list[ZonaRepartoResponse])
async def listar_zonas(
    solo_activas: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar zonas de reparto"""
    return logistica_service.get_zonas(db, solo_activas)


@router.post("/zonas", response_model=ZonaRepartoResponse)
async def crear_zona(
    zona: ZonaRepartoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Crear nueva zona de reparto"""
    return logistica_service.crear_zona(db, zona)


# ============ ENVÍOS ============
@router.get("/envios", response_model=list[EnvioResponse])
async def listar_envios(
    estado: Optional[EstadoEnvio] = None,
    fecha: Optional[date] = None,
    vehiculo_id: Optional[int] = None,
    conductor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar envíos con filtros"""
    return logistica_service.get_envios(
        db, estado, fecha, vehiculo_id, conductor_id, skip, limit
    )


@router.get("/envios/pendientes-hoy", response_model=list[EnvioResponse])
async def envios_pendientes_hoy(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar envíos pendientes para hoy"""
    return logistica_service.get_envios_pendientes_hoy(db)


@router.get("/envios/{envio_id}", response_model=EnvioResponse)
async def obtener_envio(
    envio_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener envío por ID"""
    envio = logistica_service.get_envio(db, envio_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio


@router.post("/envios/venta/{venta_id}", response_model=EnvioResponse)
async def crear_envio(
    venta_id: int,
    fecha_programada: Optional[datetime] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Crear envío para una venta"""
    try:
        return logistica_service.crear_envio_para_venta(db, venta_id, fecha_programada)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/envios/{envio_id}/asignar", response_model=EnvioResponse)
async def asignar_envio(
    envio_id: int,
    vehiculo_id: int,
    conductor_id: int,
    ruta_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Asignar vehículo y conductor a un envío"""
    try:
        return logistica_service.asignar_envio(db, envio_id, vehiculo_id, conductor_id, ruta_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/envios/{envio_id}/iniciar", response_model=EnvioResponse)
async def iniciar_envio(
    envio_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Iniciar envío (marcar en ruta)"""
    envio = logistica_service.iniciar_envio(db, envio_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio


@router.post("/envios/{envio_id}/completar", response_model=EnvioResponse)
async def completar_envio(
    envio_id: int,
    nombre_recibio: str,
    dni_recibio: Optional[str] = None,
    firma: bool = True,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    observaciones: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Completar envío (marcar como entregado)"""
    try:
        return logistica_service.completar_envio(
            db, envio_id, nombre_recibio, dni_recibio, firma, latitud, longitud, observaciones
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/envios/{envio_id}/no-entregado", response_model=EnvioResponse)
async def marcar_no_entregado(
    envio_id: int,
    motivo: str,
    reprogramar: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Marcar envío como no entregado"""
    try:
        return logistica_service.marcar_no_entregado(db, envio_id, motivo, reprogramar)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ RUTAS ============
@router.post("/rutas", response_model=RutaRepartoResponse)
async def crear_ruta(
    ruta: RutaRepartoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Crear ruta de reparto"""
    return logistica_service.crear_ruta(db, ruta)


@router.post("/rutas/{ruta_id}/completar", response_model=RutaRepartoResponse)
async def completar_ruta(
    ruta_id: int,
    kilometros: float = 0,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_logistica)
):
    """Completar ruta de reparto"""
    ruta = logistica_service.completar_ruta(db, ruta_id, kilometros)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta
