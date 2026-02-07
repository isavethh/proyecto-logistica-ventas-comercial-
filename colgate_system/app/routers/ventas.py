"""
Router de Ventas
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.usuario import Usuario
from app.models.venta import EstadoVenta
from app.schemas.venta import (
    VentaCreate, VentaUpdate, VentaResponse, VentaListResponse,
    PagoVentaCreate, PagoVentaResponse
)
from app.services import venta_service
from app.services.auth import get_usuario_actual, es_vendedor

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("", response_model=VentaListResponse)
async def listar_ventas(
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[int] = None,
    estado: Optional[EstadoVenta] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar ventas con filtros"""
    ventas, total = venta_service.get_ventas(
        db,
        skip=skip,
        limit=limit,
        cliente_id=cliente_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    return VentaListResponse(total=total, items=ventas)


@router.get("/mis-ventas", response_model=VentaListResponse)
async def mis_ventas(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[EstadoVenta] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar ventas del vendedor actual"""
    ventas, total = venta_service.get_ventas(
        db,
        skip=skip,
        limit=limit,
        vendedor_id=usuario.id,
        estado=estado
    )
    return VentaListResponse(total=total, items=ventas)


@router.get("/resumen")
async def resumen_ventas(
    fecha_desde: datetime,
    fecha_hasta: datetime,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener resumen de ventas en un período"""
    return venta_service.get_resumen_ventas(db, fecha_desde, fecha_hasta)


@router.get("/{venta_id}", response_model=VentaResponse)
async def obtener_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener venta por ID"""
    venta = venta_service.get_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.get("/numero/{numero}", response_model=VentaResponse)
async def obtener_venta_por_numero(
    numero: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener venta por número"""
    venta = venta_service.get_venta_por_numero(db, numero)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post("", response_model=VentaResponse)
async def crear_venta(
    venta: VentaCreate,
    almacen_id: int = 1,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Crear nueva venta"""
    try:
        return venta_service.crear_venta(db, venta, usuario.id, almacen_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/confirmar", response_model=VentaResponse)
async def confirmar_venta(
    venta_id: int,
    almacen_id: int = 1,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Confirmar venta y reservar inventario"""
    try:
        return venta_service.confirmar_venta(db, venta_id, almacen_id, usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/preparar", response_model=VentaResponse)
async def preparar_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Marcar venta como en preparación"""
    venta = venta_service.preparar_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post("/{venta_id}/listo-envio", response_model=VentaResponse)
async def marcar_listo_envio(
    venta_id: int,
    almacen_id: int = 1,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Marcar venta como lista para envío (descuenta inventario)"""
    try:
        return venta_service.marcar_listo_envio(db, venta_id, almacen_id, usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/cancelar", response_model=VentaResponse)
async def cancelar_venta(
    venta_id: int,
    almacen_id: int = 1,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Cancelar venta"""
    try:
        return venta_service.cancelar_venta(db, venta_id, almacen_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{venta_id}", response_model=VentaResponse)
async def actualizar_venta(
    venta_id: int,
    datos: VentaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Actualizar datos de venta"""
    venta = venta_service.get_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if venta.estado not in [EstadoVenta.BORRADOR, EstadoVenta.CONFIRMADO]:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede modificar una venta en estado {venta.estado}"
        )
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(venta, key, value)
    
    db.commit()
    db.refresh(venta)
    return venta


# ============ PAGOS ============
@router.post("/pagos", response_model=PagoVentaResponse)
async def registrar_pago(
    pago: PagoVentaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Registrar pago de una venta"""
    venta = venta_service.get_venta(db, pago.venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta_service.registrar_pago(db, pago, usuario.id)
