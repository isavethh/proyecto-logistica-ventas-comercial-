"""
Servicio de Ventas y Pedidos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.venta import Venta, DetalleVenta, PagoVenta, EstadoVenta, TipoPago
from app.models.producto import Producto
from app.models.cliente import Cliente
from app.schemas.venta import VentaCreate, VentaUpdate, DetalleVentaCreate, PagoVentaCreate
from app.services import inventario_service
from app.models.inventario import TipoMovimiento


def generar_numero_venta(db: Session) -> str:
    """Genera un número único de venta"""
    hoy = datetime.utcnow()
    prefijo = f"V{hoy.strftime('%Y%m')}"
    
    ultima = db.query(Venta).filter(
        Venta.numero.like(f"{prefijo}%")
    ).order_by(Venta.numero.desc()).first()
    
    if ultima:
        ultimo_numero = int(ultima.numero[-5:])
        nuevo_numero = ultimo_numero + 1
    else:
        nuevo_numero = 1
    
    return f"{prefijo}{nuevo_numero:05d}"


def get_ventas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[int] = None,
    vendedor_id: Optional[int] = None,
    estado: Optional[EstadoVenta] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> tuple[List[Venta], int]:
    query = db.query(Venta)
    
    if cliente_id:
        query = query.filter(Venta.cliente_id == cliente_id)
    if vendedor_id:
        query = query.filter(Venta.vendedor_id == vendedor_id)
    if estado:
        query = query.filter(Venta.estado == estado)
    if fecha_desde:
        query = query.filter(Venta.fecha_pedido >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Venta.fecha_pedido <= fecha_hasta)
    
    total = query.count()
    ventas = query.order_by(Venta.fecha_pedido.desc()).offset(skip).limit(limit).all()
    return ventas, total


def get_venta(db: Session, venta_id: int) -> Optional[Venta]:
    return db.query(Venta).filter(Venta.id == venta_id).first()


def get_venta_por_numero(db: Session, numero: str) -> Optional[Venta]:
    return db.query(Venta).filter(Venta.numero == numero).first()


def crear_venta(db: Session, venta: VentaCreate, vendedor_id: int, almacen_id: int = 1) -> Venta:
    """Crea una nueva venta con sus detalles"""
    
    # Crear venta
    numero = generar_numero_venta(db)
    db_venta = Venta(
        numero=numero,
        cliente_id=venta.cliente_id,
        vendedor_id=vendedor_id,
        tipo_documento=venta.tipo_documento,
        tipo_pago=venta.tipo_pago,
        fecha_entrega_solicitada=venta.fecha_entrega_solicitada,
        direccion_entrega=venta.direccion_entrega,
        referencia_entrega=venta.referencia_entrega,
        observaciones=venta.observaciones,
        estado=EstadoVenta.BORRADOR
    )
    db.add(db_venta)
    db.flush()
    
    # Agregar detalles
    subtotal = 0
    for detalle in venta.detalles:
        producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
        if not producto:
            raise ValueError(f"Producto {detalle.producto_id} no encontrado")
        
        precio_final = detalle.precio_unitario * (1 - detalle.descuento_porcentaje / 100)
        subtotal_detalle = (precio_final * detalle.cantidad) - detalle.descuento_monto
        
        db_detalle = DetalleVenta(
            venta_id=db_venta.id,
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            descuento_porcentaje=detalle.descuento_porcentaje,
            descuento_monto=detalle.descuento_monto,
            subtotal=subtotal_detalle
        )
        db.add(db_detalle)
        subtotal += subtotal_detalle
    
    # Calcular totales
    db_venta.subtotal = subtotal
    db_venta.impuesto = subtotal * 0.18  # IGV 18%
    db_venta.total = db_venta.subtotal + db_venta.impuesto - db_venta.descuento
    
    # Calcular fecha vencimiento si es crédito
    if venta.tipo_pago == TipoPago.CREDITO:
        cliente = db.query(Cliente).filter(Cliente.id == venta.cliente_id).first()
        if cliente and cliente.dias_credito > 0:
            db_venta.fecha_vencimiento_pago = datetime.utcnow() + timedelta(days=cliente.dias_credito)
    
    db.commit()
    db.refresh(db_venta)
    return db_venta


def confirmar_venta(db: Session, venta_id: int, almacen_id: int = 1, usuario_id: int = None) -> Venta:
    """Confirma una venta y reserva el inventario"""
    venta = get_venta(db, venta_id)
    if not venta:
        raise ValueError("Venta no encontrada")
    
    if venta.estado != EstadoVenta.BORRADOR:
        raise ValueError(f"La venta no puede ser confirmada. Estado actual: {venta.estado}")
    
    # Verificar y reservar stock
    for detalle in venta.detalles:
        stock_disponible = inventario_service.get_stock_disponible_producto(db, detalle.producto_id)
        if stock_disponible < detalle.cantidad:
            producto = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
            raise ValueError(f"Stock insuficiente para {producto.nombre}. Disponible: {stock_disponible}, Requerido: {detalle.cantidad}")
        
        inventario_service.reservar_stock(db, detalle.producto_id, almacen_id, detalle.cantidad)
    
    venta.estado = EstadoVenta.CONFIRMADO
    db.commit()
    db.refresh(venta)
    return venta


def preparar_venta(db: Session, venta_id: int) -> Venta:
    """Marca la venta como en preparación"""
    venta = get_venta(db, venta_id)
    if venta and venta.estado == EstadoVenta.CONFIRMADO:
        venta.estado = EstadoVenta.EN_PREPARACION
        db.commit()
        db.refresh(venta)
    return venta


def marcar_listo_envio(db: Session, venta_id: int, almacen_id: int = 1, usuario_id: int = None) -> Venta:
    """Marca la venta como lista para envío y descuenta del inventario"""
    venta = get_venta(db, venta_id)
    if not venta:
        raise ValueError("Venta no encontrada")
    
    if venta.estado != EstadoVenta.EN_PREPARACION:
        raise ValueError(f"La venta no está en preparación. Estado: {venta.estado}")
    
    # Descontar inventario
    for detalle in venta.detalles:
        inventario_service.registrar_movimiento(
            db=db,
            almacen_id=almacen_id,
            producto_id=detalle.producto_id,
            tipo=TipoMovimiento.SALIDA_VENTA,
            cantidad=detalle.cantidad,
            usuario_id=usuario_id,
            documento_tipo="venta",
            documento_id=venta.id,
            documento_numero=venta.numero
        )
        # Liberar reserva
        inventario_service.liberar_reserva(db, detalle.producto_id, almacen_id, detalle.cantidad)
    
    venta.estado = EstadoVenta.LISTO_ENVIO
    db.commit()
    db.refresh(venta)
    return venta


def cancelar_venta(db: Session, venta_id: int, almacen_id: int = 1) -> Venta:
    """Cancela una venta y libera el inventario reservado"""
    venta = get_venta(db, venta_id)
    if not venta:
        raise ValueError("Venta no encontrada")
    
    if venta.estado in [EstadoVenta.ENTREGADO, EstadoVenta.CANCELADO]:
        raise ValueError(f"La venta no puede ser cancelada. Estado: {venta.estado}")
    
    # Si ya estaba confirmada, liberar reservas
    if venta.estado in [EstadoVenta.CONFIRMADO, EstadoVenta.EN_PREPARACION]:
        for detalle in venta.detalles:
            inventario_service.liberar_reserva(db, detalle.producto_id, almacen_id, detalle.cantidad)
    
    venta.estado = EstadoVenta.CANCELADO
    db.commit()
    db.refresh(venta)
    return venta


def registrar_pago(db: Session, pago: PagoVentaCreate, usuario_id: int) -> PagoVenta:
    """Registra un pago para una venta"""
    db_pago = PagoVenta(
        venta_id=pago.venta_id,
        monto=pago.monto,
        tipo_pago=pago.tipo_pago,
        referencia=pago.referencia,
        usuario_id=usuario_id
    )
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago


def get_resumen_ventas(db: Session, fecha_desde: datetime, fecha_hasta: datetime) -> dict:
    """Obtiene resumen de ventas en un período"""
    ventas = db.query(Venta).filter(
        Venta.fecha_pedido >= fecha_desde,
        Venta.fecha_pedido <= fecha_hasta,
        Venta.estado != EstadoVenta.CANCELADO
    ).all()
    
    total_ventas = sum(v.total for v in ventas)
    cantidad_ventas = len(ventas)
    
    return {
        "periodo": {
            "desde": fecha_desde.isoformat(),
            "hasta": fecha_hasta.isoformat()
        },
        "total_ventas": total_ventas,
        "cantidad_pedidos": cantidad_ventas,
        "promedio_pedido": total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0,
        "por_estado": {
            estado.value: len([v for v in ventas if v.estado == estado])
            for estado in EstadoVenta
        }
    }
