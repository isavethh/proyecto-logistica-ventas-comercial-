"""
Servicio de Inventario y Movimientos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.inventario import Inventario, MovimientoInventario, Almacen, TipoMovimiento, TipoAlmacen
from app.models.producto import Producto
from app.schemas.inventario import (
    InventarioCreate, InventarioUpdate,
    AlmacenCreate, AlmacenUpdate,
    MovimientoCreate, AjusteInventario, TransferenciaInventario
)


# ============ ALMACÉN ============
def get_almacenes(db: Session, solo_activos: bool = True) -> List[Almacen]:
    query = db.query(Almacen)
    if solo_activos:
        query = query.filter(Almacen.activo == True)
    return query.all()


def get_almacen(db: Session, almacen_id: int) -> Optional[Almacen]:
    return db.query(Almacen).filter(Almacen.id == almacen_id).first()


def crear_almacen(db: Session, almacen: AlmacenCreate) -> Almacen:
    db_almacen = Almacen(**almacen.model_dump())
    db.add(db_almacen)
    db.commit()
    db.refresh(db_almacen)
    return db_almacen


def actualizar_almacen(db: Session, almacen_id: int, almacen: AlmacenUpdate) -> Optional[Almacen]:
    db_almacen = get_almacen(db, almacen_id)
    if db_almacen:
        for key, value in almacen.model_dump(exclude_unset=True).items():
            setattr(db_almacen, key, value)
        db.commit()
        db.refresh(db_almacen)
    return db_almacen


# ============ INVENTARIO ============
def get_inventario_producto(db: Session, producto_id: int, almacen_id: Optional[int] = None) -> List[Inventario]:
    query = db.query(Inventario).filter(Inventario.producto_id == producto_id)
    if almacen_id:
        query = query.filter(Inventario.almacen_id == almacen_id)
    return query.all()


def get_inventario_almacen(db: Session, almacen_id: int) -> List[Inventario]:
    return db.query(Inventario).filter(Inventario.almacen_id == almacen_id).all()


def get_stock_total_producto(db: Session, producto_id: int) -> int:
    result = db.query(func.sum(Inventario.stock_actual)).filter(
        Inventario.producto_id == producto_id
    ).scalar()
    return result or 0


def get_stock_disponible_producto(db: Session, producto_id: int) -> int:
    result = db.query(func.sum(Inventario.stock_disponible)).filter(
        Inventario.producto_id == producto_id
    ).scalar()
    return result or 0


def get_o_crear_inventario(db: Session, producto_id: int, almacen_id: int) -> Inventario:
    """Obtiene o crea un registro de inventario para producto en almacén"""
    inventario = db.query(Inventario).filter(
        Inventario.producto_id == producto_id,
        Inventario.almacen_id == almacen_id
    ).first()
    
    if not inventario:
        inventario = Inventario(
            producto_id=producto_id,
            almacen_id=almacen_id,
            stock_actual=0,
            stock_reservado=0,
            stock_disponible=0
        )
        db.add(inventario)
        db.commit()
        db.refresh(inventario)
    
    return inventario


def registrar_movimiento(
    db: Session,
    almacen_id: int,
    producto_id: int,
    tipo: TipoMovimiento,
    cantidad: int,
    usuario_id: Optional[int] = None,
    documento_tipo: Optional[str] = None,
    documento_id: Optional[int] = None,
    documento_numero: Optional[str] = None,
    motivo: Optional[str] = None
) -> MovimientoInventario:
    """Registra un movimiento de inventario y actualiza el stock"""
    
    # Obtener o crear inventario
    inventario = get_o_crear_inventario(db, producto_id, almacen_id)
    stock_anterior = inventario.stock_actual
    
    # Determinar si es entrada o salida
    es_entrada = tipo.value.startswith('entrada')
    
    if es_entrada:
        inventario.stock_actual += cantidad
    else:
        if inventario.stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {inventario.stock_actual}, Solicitado: {cantidad}")
        inventario.stock_actual -= cantidad
    
    inventario.stock_disponible = inventario.stock_actual - inventario.stock_reservado
    
    # Crear movimiento
    movimiento = MovimientoInventario(
        almacen_id=almacen_id,
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_posterior=inventario.stock_actual,
        documento_tipo=documento_tipo,
        documento_id=documento_id,
        documento_numero=documento_numero,
        motivo=motivo,
        usuario_id=usuario_id
    )
    
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    
    return movimiento


def ajustar_inventario(db: Session, ajuste: AjusteInventario, usuario_id: int) -> MovimientoInventario:
    """Realiza un ajuste de inventario (positivo o negativo)"""
    tipo = TipoMovimiento.ENTRADA_AJUSTE if ajuste.cantidad > 0 else TipoMovimiento.SALIDA_AJUSTE
    cantidad = abs(ajuste.cantidad)
    
    return registrar_movimiento(
        db=db,
        almacen_id=ajuste.almacen_id,
        producto_id=ajuste.producto_id,
        tipo=tipo,
        cantidad=cantidad,
        usuario_id=usuario_id,
        documento_tipo="ajuste",
        motivo=ajuste.motivo
    )


def transferir_inventario(db: Session, transferencia: TransferenciaInventario, usuario_id: int) -> tuple:
    """Transfiere inventario entre almacenes"""
    # Salida del almacén origen
    mov_salida = registrar_movimiento(
        db=db,
        almacen_id=transferencia.almacen_origen_id,
        producto_id=transferencia.producto_id,
        tipo=TipoMovimiento.SALIDA_TRANSFERENCIA,
        cantidad=transferencia.cantidad,
        usuario_id=usuario_id,
        documento_tipo="transferencia",
        motivo=transferencia.motivo
    )
    
    # Entrada al almacén destino
    mov_entrada = registrar_movimiento(
        db=db,
        almacen_id=transferencia.almacen_destino_id,
        producto_id=transferencia.producto_id,
        tipo=TipoMovimiento.ENTRADA_TRANSFERENCIA,
        cantidad=transferencia.cantidad,
        usuario_id=usuario_id,
        documento_tipo="transferencia",
        motivo=transferencia.motivo
    )
    
    return mov_salida, mov_entrada


def reservar_stock(db: Session, producto_id: int, almacen_id: int, cantidad: int) -> bool:
    """Reserva stock para un pedido"""
    inventario = get_o_crear_inventario(db, producto_id, almacen_id)
    
    if inventario.stock_disponible < cantidad:
        return False
    
    inventario.stock_reservado += cantidad
    inventario.stock_disponible = inventario.stock_actual - inventario.stock_reservado
    db.commit()
    return True


def liberar_reserva(db: Session, producto_id: int, almacen_id: int, cantidad: int):
    """Libera stock reservado"""
    inventario = get_o_crear_inventario(db, producto_id, almacen_id)
    inventario.stock_reservado = max(0, inventario.stock_reservado - cantidad)
    inventario.stock_disponible = inventario.stock_actual - inventario.stock_reservado
    db.commit()


def get_movimientos(
    db: Session,
    almacen_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    tipo: Optional[TipoMovimiento] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[MovimientoInventario]:
    query = db.query(MovimientoInventario)
    
    if almacen_id:
        query = query.filter(MovimientoInventario.almacen_id == almacen_id)
    if producto_id:
        query = query.filter(MovimientoInventario.producto_id == producto_id)
    if tipo:
        query = query.filter(MovimientoInventario.tipo == tipo)
    if fecha_desde:
        query = query.filter(MovimientoInventario.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(MovimientoInventario.fecha <= fecha_hasta)
    
    return query.order_by(MovimientoInventario.fecha.desc()).offset(skip).limit(limit).all()


def get_productos_por_vencer(db: Session, dias: int = 90) -> List[Inventario]:
    """Obtiene productos que vencen en los próximos X días"""
    from datetime import timedelta
    fecha_limite = datetime.utcnow() + timedelta(days=dias)
    
    return db.query(Inventario).filter(
        Inventario.fecha_vencimiento != None,
        Inventario.fecha_vencimiento <= fecha_limite,
        Inventario.stock_actual > 0
    ).all()
