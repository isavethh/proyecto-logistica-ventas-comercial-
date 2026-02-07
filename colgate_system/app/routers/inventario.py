"""
Router de Inventario
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.usuario import Usuario
from app.models.inventario import TipoMovimiento
from app.schemas.inventario import (
    AlmacenCreate, AlmacenUpdate, AlmacenResponse,
    InventarioResponse, MovimientoResponse,
    AjusteInventario, TransferenciaInventario
)
from app.services import inventario_service
from app.services.auth import get_usuario_actual, es_almacenero

router = APIRouter(prefix="/inventario", tags=["Inventario"])


# ============ ALMACENES ============
@router.get("/almacenes", response_model=list[AlmacenResponse])
async def listar_almacenes(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar todos los almacenes"""
    return inventario_service.get_almacenes(db, solo_activos=solo_activos)


@router.get("/almacenes/{almacen_id}", response_model=AlmacenResponse)
async def obtener_almacen(
    almacen_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener almacén por ID"""
    almacen = inventario_service.get_almacen(db, almacen_id)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return almacen


@router.post("/almacenes", response_model=AlmacenResponse)
async def crear_almacen(
    almacen: AlmacenCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_almacenero)
):
    """Crear nuevo almacén"""
    return inventario_service.crear_almacen(db, almacen)


@router.put("/almacenes/{almacen_id}", response_model=AlmacenResponse)
async def actualizar_almacen(
    almacen_id: int,
    almacen: AlmacenUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_almacenero)
):
    """Actualizar almacén"""
    resultado = inventario_service.actualizar_almacen(db, almacen_id, almacen)
    if not resultado:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return resultado


# ============ INVENTARIO ============
@router.get("/producto/{producto_id}", response_model=list[InventarioResponse])
async def stock_producto(
    producto_id: int,
    almacen_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener inventario de un producto"""
    return inventario_service.get_inventario_producto(db, producto_id, almacen_id)


@router.get("/producto/{producto_id}/total")
async def stock_total_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener stock total de un producto (todos los almacenes)"""
    total = inventario_service.get_stock_total_producto(db, producto_id)
    disponible = inventario_service.get_stock_disponible_producto(db, producto_id)
    return {
        "producto_id": producto_id,
        "stock_total": total,
        "stock_disponible": disponible
    }


@router.get("/almacen/{almacen_id}", response_model=list[InventarioResponse])
async def inventario_almacen(
    almacen_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener inventario completo de un almacén"""
    return inventario_service.get_inventario_almacen(db, almacen_id)


@router.get("/por-vencer", response_model=list[InventarioResponse])
async def productos_por_vencer(
    dias: int = 90,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener productos que vencen en los próximos X días"""
    return inventario_service.get_productos_por_vencer(db, dias)


# ============ AJUSTES ============
@router.post("/ajuste", response_model=MovimientoResponse)
async def ajustar_inventario(
    ajuste: AjusteInventario,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_almacenero)
):
    """Realizar ajuste de inventario"""
    try:
        return inventario_service.ajustar_inventario(db, ajuste, usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transferencia")
async def transferir_inventario(
    transferencia: TransferenciaInventario,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_almacenero)
):
    """Transferir inventario entre almacenes"""
    try:
        mov_salida, mov_entrada = inventario_service.transferir_inventario(
            db, transferencia, usuario.id
        )
        return {
            "mensaje": "Transferencia exitosa",
            "movimiento_salida": mov_salida.id,
            "movimiento_entrada": mov_entrada.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ MOVIMIENTOS ============
@router.get("/movimientos", response_model=list[MovimientoResponse])
async def listar_movimientos(
    almacen_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    tipo: Optional[TipoMovimiento] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar movimientos de inventario"""
    return inventario_service.get_movimientos(
        db,
        almacen_id=almacen_id,
        producto_id=producto_id,
        tipo=tipo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        skip=skip,
        limit=limit
    )
