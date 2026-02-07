"""
Servicio CRUD de Clientes
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.cliente import Cliente, TipoCliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


def get_clientes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    solo_activos: bool = True,
    tipo: Optional[TipoCliente] = None,
    busqueda: Optional[str] = None,
    distrito: Optional[str] = None
) -> tuple[List[Cliente], int]:
    query = db.query(Cliente)
    
    if solo_activos:
        query = query.filter(Cliente.activo == True)
    if tipo:
        query = query.filter(Cliente.tipo == tipo)
    if distrito:
        query = query.filter(Cliente.distrito.ilike(f"%{distrito}%"))
    if busqueda:
        query = query.filter(
            or_(
                Cliente.razon_social.ilike(f"%{busqueda}%"),
                Cliente.nombre_comercial.ilike(f"%{busqueda}%"),
                Cliente.codigo.ilike(f"%{busqueda}%"),
                Cliente.ruc.ilike(f"%{busqueda}%")
            )
        )
    
    total = query.count()
    clientes = query.offset(skip).limit(limit).all()
    return clientes, total


def get_cliente(db: Session, cliente_id: int) -> Optional[Cliente]:
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def get_cliente_por_codigo(db: Session, codigo: str) -> Optional[Cliente]:
    return db.query(Cliente).filter(Cliente.codigo == codigo).first()


def get_cliente_por_ruc(db: Session, ruc: str) -> Optional[Cliente]:
    return db.query(Cliente).filter(Cliente.ruc == ruc).first()


def crear_cliente(db: Session, cliente: ClienteCreate) -> Cliente:
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


def actualizar_cliente(db: Session, cliente_id: int, cliente: ClienteUpdate) -> Optional[Cliente]:
    db_cliente = get_cliente(db, cliente_id)
    if db_cliente:
        for key, value in cliente.model_dump(exclude_unset=True).items():
            setattr(db_cliente, key, value)
        db.commit()
        db.refresh(db_cliente)
    return db_cliente


def eliminar_cliente(db: Session, cliente_id: int) -> bool:
    """Eliminación lógica del cliente"""
    db_cliente = get_cliente(db, cliente_id)
    if db_cliente:
        db_cliente.activo = False
        db.commit()
        return True
    return False


def get_clientes_por_zona(db: Session, distrito: str) -> List[Cliente]:
    """Obtiene clientes de un distrito específico"""
    return db.query(Cliente).filter(
        Cliente.activo == True,
        Cliente.distrito.ilike(f"%{distrito}%")
    ).all()


def get_clientes_con_credito_vencido(db: Session) -> List[Cliente]:
    """Obtiene clientes con facturas vencidas pendientes"""
    from app.models.venta import Venta, EstadoVenta
    from datetime import datetime
    
    return db.query(Cliente).join(Venta).filter(
        Venta.estado.in_([EstadoVenta.CONFIRMADO, EstadoVenta.ENTREGADO]),
        Venta.fecha_vencimiento_pago < datetime.utcnow(),
        Venta.total > 0  # Pendiente de pago completo
    ).distinct().all()
