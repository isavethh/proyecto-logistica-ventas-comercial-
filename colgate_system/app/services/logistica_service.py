"""
Servicio de Logística - Envíos, Rutas y Distribución
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.logistica import (
    Vehiculo, Conductor, ZonaReparto, RutaReparto, Envio, RutaCliente,
    EstadoEnvio, TipoVehiculo
)
from app.models.venta import Venta, EstadoVenta
from app.schemas.logistica import (
    VehiculoCreate, VehiculoUpdate,
    ConductorCreate, ConductorUpdate,
    ZonaRepartoCreate, ZonaRepartoUpdate,
    RutaRepartoCreate, RutaRepartoUpdate,
    EnvioCreate, EnvioUpdate
)


def generar_codigo_envio(db: Session) -> str:
    """Genera código único de envío"""
    hoy = datetime.utcnow()
    prefijo = f"ENV{hoy.strftime('%Y%m%d')}"
    
    ultimo = db.query(Envio).filter(
        Envio.codigo.like(f"{prefijo}%")
    ).order_by(Envio.codigo.desc()).first()
    
    if ultimo:
        num = int(ultimo.codigo[-4:]) + 1
    else:
        num = 1
    
    return f"{prefijo}{num:04d}"


def generar_codigo_ruta(db: Session) -> str:
    """Genera código único de ruta"""
    hoy = datetime.utcnow()
    prefijo = f"RUT{hoy.strftime('%Y%m%d')}"
    
    ultima = db.query(RutaReparto).filter(
        RutaReparto.codigo.like(f"{prefijo}%")
    ).order_by(RutaReparto.codigo.desc()).first()
    
    if ultima:
        num = int(ultima.codigo[-3:]) + 1
    else:
        num = 1
    
    return f"{prefijo}{num:03d}"


# ============ VEHÍCULOS ============
def get_vehiculos(db: Session, solo_activos: bool = True, solo_disponibles: bool = False) -> List[Vehiculo]:
    query = db.query(Vehiculo)
    if solo_activos:
        query = query.filter(Vehiculo.activo == True)
    if solo_disponibles:
        query = query.filter(Vehiculo.disponible == True)
    return query.all()


def get_vehiculo(db: Session, vehiculo_id: int) -> Optional[Vehiculo]:
    return db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()


def crear_vehiculo(db: Session, vehiculo: VehiculoCreate) -> Vehiculo:
    db_vehiculo = Vehiculo(**vehiculo.model_dump())
    db.add(db_vehiculo)
    db.commit()
    db.refresh(db_vehiculo)
    return db_vehiculo


def actualizar_vehiculo(db: Session, vehiculo_id: int, vehiculo: VehiculoUpdate) -> Optional[Vehiculo]:
    db_vehiculo = get_vehiculo(db, vehiculo_id)
    if db_vehiculo:
        for key, value in vehiculo.model_dump(exclude_unset=True).items():
            setattr(db_vehiculo, key, value)
        db.commit()
        db.refresh(db_vehiculo)
    return db_vehiculo


# ============ CONDUCTORES ============
def get_conductores(db: Session, solo_activos: bool = True, solo_disponibles: bool = False) -> List[Conductor]:
    query = db.query(Conductor)
    if solo_activos:
        query = query.filter(Conductor.activo == True)
    if solo_disponibles:
        query = query.filter(Conductor.disponible == True)
    return query.all()


def get_conductor(db: Session, conductor_id: int) -> Optional[Conductor]:
    return db.query(Conductor).filter(Conductor.id == conductor_id).first()


def crear_conductor(db: Session, conductor: ConductorCreate) -> Conductor:
    db_conductor = Conductor(**conductor.model_dump())
    db.add(db_conductor)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor


def actualizar_conductor(db: Session, conductor_id: int, conductor: ConductorUpdate) -> Optional[Conductor]:
    db_conductor = get_conductor(db, conductor_id)
    if db_conductor:
        for key, value in conductor.model_dump(exclude_unset=True).items():
            setattr(db_conductor, key, value)
        db.commit()
        db.refresh(db_conductor)
    return db_conductor


# ============ ZONAS ============
def get_zonas(db: Session, solo_activas: bool = True) -> List[ZonaReparto]:
    query = db.query(ZonaReparto)
    if solo_activas:
        query = query.filter(ZonaReparto.activo == True)
    return query.all()


def get_zona(db: Session, zona_id: int) -> Optional[ZonaReparto]:
    return db.query(ZonaReparto).filter(ZonaReparto.id == zona_id).first()


def crear_zona(db: Session, zona: ZonaRepartoCreate) -> ZonaReparto:
    db_zona = ZonaReparto(**zona.model_dump())
    db.add(db_zona)
    db.commit()
    db.refresh(db_zona)
    return db_zona


# ============ ENVÍOS ============
def get_envios(
    db: Session,
    estado: Optional[EstadoEnvio] = None,
    fecha: Optional[date] = None,
    vehiculo_id: Optional[int] = None,
    conductor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Envio]:
    query = db.query(Envio)
    
    if estado:
        query = query.filter(Envio.estado == estado)
    if fecha:
        query = query.filter(func.date(Envio.fecha_programada) == fecha)
    if vehiculo_id:
        query = query.filter(Envio.vehiculo_id == vehiculo_id)
    if conductor_id:
        query = query.filter(Envio.conductor_id == conductor_id)
    
    return query.order_by(Envio.fecha_programada).offset(skip).limit(limit).all()


def get_envio(db: Session, envio_id: int) -> Optional[Envio]:
    return db.query(Envio).filter(Envio.id == envio_id).first()


def crear_envio_para_venta(db: Session, venta_id: int, fecha_programada: Optional[datetime] = None) -> Envio:
    """Crea un envío para una venta"""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise ValueError("Venta no encontrada")
    
    if venta.estado not in [EstadoVenta.LISTO_ENVIO, EstadoVenta.CONFIRMADO]:
        raise ValueError(f"La venta no está lista para envío. Estado: {venta.estado}")
    
    codigo = generar_codigo_envio(db)
    envio = Envio(
        codigo=codigo,
        venta_id=venta_id,
        fecha_programada=fecha_programada or venta.fecha_entrega_solicitada,
        estado=EstadoEnvio.PENDIENTE
    )
    db.add(envio)
    db.commit()
    db.refresh(envio)
    return envio


def asignar_envio(
    db: Session,
    envio_id: int,
    vehiculo_id: int,
    conductor_id: int,
    ruta_id: Optional[int] = None
) -> Envio:
    """Asigna vehículo y conductor a un envío"""
    envio = get_envio(db, envio_id)
    if not envio:
        raise ValueError("Envío no encontrado")
    
    envio.vehiculo_id = vehiculo_id
    envio.conductor_id = conductor_id
    envio.ruta_id = ruta_id
    envio.estado = EstadoEnvio.ASIGNADO
    
    db.commit()
    db.refresh(envio)
    return envio


def iniciar_envio(db: Session, envio_id: int) -> Envio:
    """Marca el envío como en ruta"""
    envio = get_envio(db, envio_id)
    if envio and envio.estado == EstadoEnvio.ASIGNADO:
        envio.estado = EstadoEnvio.EN_RUTA
        # Actualizar venta
        if envio.venta:
            envio.venta.estado = EstadoVenta.EN_RUTA
        db.commit()
        db.refresh(envio)
    return envio


def completar_envio(
    db: Session,
    envio_id: int,
    nombre_recibio: str,
    dni_recibio: Optional[str] = None,
    firma: bool = True,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    observaciones: Optional[str] = None
) -> Envio:
    """Marca el envío como entregado"""
    envio = get_envio(db, envio_id)
    if not envio:
        raise ValueError("Envío no encontrado")
    
    envio.estado = EstadoEnvio.ENTREGADO
    envio.fecha_entrega = datetime.utcnow()
    envio.nombre_recibio = nombre_recibio
    envio.dni_recibio = dni_recibio
    envio.firma_recibido = firma
    envio.latitud_entrega = latitud
    envio.longitud_entrega = longitud
    if observaciones:
        envio.observaciones = observaciones
    
    # Actualizar venta
    if envio.venta:
        envio.venta.estado = EstadoVenta.ENTREGADO
        envio.venta.fecha_entrega_real = datetime.utcnow()
    
    # Actualizar ruta si existe
    if envio.ruta:
        envio.ruta.entregas_exitosas += 1
    
    db.commit()
    db.refresh(envio)
    return envio


def marcar_no_entregado(
    db: Session,
    envio_id: int,
    motivo: str,
    reprogramar: bool = True
) -> Envio:
    """Marca el envío como no entregado"""
    envio = get_envio(db, envio_id)
    if not envio:
        raise ValueError("Envío no encontrado")
    
    envio.estado = EstadoEnvio.REPROGRAMADO if reprogramar else EstadoEnvio.NO_ENTREGADO
    envio.motivo_no_entrega = motivo
    
    # Actualizar ruta si existe
    if envio.ruta:
        envio.ruta.entregas_fallidas += 1
    
    db.commit()
    db.refresh(envio)
    return envio


# ============ RUTAS ============
def crear_ruta(db: Session, ruta: RutaRepartoCreate) -> RutaReparto:
    """Crea una ruta de reparto"""
    codigo = generar_codigo_ruta(db)
    db_ruta = RutaReparto(
        codigo=codigo,
        nombre=ruta.nombre,
        fecha=ruta.fecha,
        zona_id=ruta.zona_id,
        vehiculo_id=ruta.vehiculo_id,
        conductor_id=ruta.conductor_id
    )
    db.add(db_ruta)
    db.flush()
    
    # Asignar envíos a la ruta
    for orden, envio_id in enumerate(ruta.envio_ids, 1):
        envio = get_envio(db, envio_id)
        if envio:
            envio.ruta_id = db_ruta.id
            envio.orden_entrega = orden
            envio.vehiculo_id = ruta.vehiculo_id
            envio.conductor_id = ruta.conductor_id
            envio.estado = EstadoEnvio.ASIGNADO
    
    db_ruta.total_entregas = len(ruta.envio_ids)
    
    # Marcar vehículo y conductor como no disponibles
    if ruta.vehiculo_id:
        vehiculo = get_vehiculo(db, ruta.vehiculo_id)
        if vehiculo:
            vehiculo.disponible = False
    if ruta.conductor_id:
        conductor = get_conductor(db, ruta.conductor_id)
        if conductor:
            conductor.disponible = False
    
    db.commit()
    db.refresh(db_ruta)
    return db_ruta


def completar_ruta(db: Session, ruta_id: int, kilometros: float = 0) -> RutaReparto:
    """Marca una ruta como completada"""
    ruta = db.query(RutaReparto).filter(RutaReparto.id == ruta_id).first()
    if ruta:
        ruta.completada = True
        ruta.hora_retorno = datetime.utcnow().time()
        ruta.kilometros_recorridos = kilometros
        
        # Liberar vehículo y conductor
        if ruta.vehiculo:
            ruta.vehiculo.disponible = True
        if ruta.conductor:
            ruta.conductor.disponible = True
        
        db.commit()
        db.refresh(ruta)
    return ruta


def get_envios_pendientes_hoy(db: Session) -> List[Envio]:
    """Obtiene envíos pendientes para hoy"""
    hoy = date.today()
    return db.query(Envio).filter(
        Envio.estado.in_([EstadoEnvio.PENDIENTE, EstadoEnvio.ASIGNADO]),
        func.date(Envio.fecha_programada) == hoy
    ).all()


def get_dashboard_logistica(db: Session) -> dict:
    """Dashboard de logística"""
    from sqlalchemy import func
    
    hoy = date.today()
    
    # Envíos de hoy
    envios_hoy = db.query(Envio).filter(
        func.date(Envio.fecha_programada) == hoy
    ).all()
    
    # Vehículos disponibles
    vehiculos_disponibles = db.query(Vehiculo).filter(
        Vehiculo.activo == True,
        Vehiculo.disponible == True
    ).count()
    
    # Conductores disponibles
    conductores_disponibles = db.query(Conductor).filter(
        Conductor.activo == True,
        Conductor.disponible == True
    ).count()
    
    return {
        "fecha": hoy.isoformat(),
        "envios": {
            "total": len(envios_hoy),
            "pendientes": len([e for e in envios_hoy if e.estado == EstadoEnvio.PENDIENTE]),
            "asignados": len([e for e in envios_hoy if e.estado == EstadoEnvio.ASIGNADO]),
            "en_ruta": len([e for e in envios_hoy if e.estado == EstadoEnvio.EN_RUTA]),
            "entregados": len([e for e in envios_hoy if e.estado == EstadoEnvio.ENTREGADO]),
            "no_entregados": len([e for e in envios_hoy if e.estado == EstadoEnvio.NO_ENTREGADO])
        },
        "recursos": {
            "vehiculos_disponibles": vehiculos_disponibles,
            "conductores_disponibles": conductores_disponibles
        }
    }


# Importación necesaria para func
from sqlalchemy import func
