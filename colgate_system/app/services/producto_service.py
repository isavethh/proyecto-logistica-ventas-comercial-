"""
Servicio CRUD de Productos, Categorías y Marcas
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.producto import Producto, UnidadMedida
from app.models.categoria import Categoria, Marca
from app.schemas.producto import (
    ProductoCreate, ProductoUpdate,
    CategoriaCreate, CategoriaUpdate,
    MarcaCreate, MarcaUpdate
)


# ============ CATEGORÍA ============
def get_categorias(db: Session, skip: int = 0, limit: int = 100, solo_activos: bool = True) -> List[Categoria]:
    query = db.query(Categoria)
    if solo_activos:
        query = query.filter(Categoria.activo == True)
    return query.offset(skip).limit(limit).all()


def get_categoria(db: Session, categoria_id: int) -> Optional[Categoria]:
    return db.query(Categoria).filter(Categoria.id == categoria_id).first()


def get_categoria_por_codigo(db: Session, codigo: str) -> Optional[Categoria]:
    return db.query(Categoria).filter(Categoria.codigo == codigo).first()


def crear_categoria(db: Session, categoria: CategoriaCreate) -> Categoria:
    db_categoria = Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria


def actualizar_categoria(db: Session, categoria_id: int, categoria: CategoriaUpdate) -> Optional[Categoria]:
    db_categoria = get_categoria(db, categoria_id)
    if db_categoria:
        for key, value in categoria.model_dump(exclude_unset=True).items():
            setattr(db_categoria, key, value)
        db.commit()
        db.refresh(db_categoria)
    return db_categoria


# ============ MARCA ============
def get_marcas(db: Session, skip: int = 0, limit: int = 100, solo_activos: bool = True) -> List[Marca]:
    query = db.query(Marca)
    if solo_activos:
        query = query.filter(Marca.activo == True)
    return query.offset(skip).limit(limit).all()


def get_marca(db: Session, marca_id: int) -> Optional[Marca]:
    return db.query(Marca).filter(Marca.id == marca_id).first()


def crear_marca(db: Session, marca: MarcaCreate) -> Marca:
    db_marca = Marca(**marca.model_dump())
    db.add(db_marca)
    db.commit()
    db.refresh(db_marca)
    return db_marca


def actualizar_marca(db: Session, marca_id: int, marca: MarcaUpdate) -> Optional[Marca]:
    db_marca = get_marca(db, marca_id)
    if db_marca:
        for key, value in marca.model_dump(exclude_unset=True).items():
            setattr(db_marca, key, value)
        db.commit()
        db.refresh(db_marca)
    return db_marca


# ============ PRODUCTO ============
def get_productos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    solo_activos: bool = True,
    categoria_id: Optional[int] = None,
    marca_id: Optional[int] = None,
    busqueda: Optional[str] = None
) -> tuple[List[Producto], int]:
    query = db.query(Producto)
    
    if solo_activos:
        query = query.filter(Producto.activo == True)
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)
    if marca_id:
        query = query.filter(Producto.marca_id == marca_id)
    if busqueda:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{busqueda}%"),
                Producto.codigo.ilike(f"%{busqueda}%"),
                Producto.codigo_barras.ilike(f"%{busqueda}%")
            )
        )
    
    total = query.count()
    productos = query.offset(skip).limit(limit).all()
    return productos, total


def get_producto(db: Session, producto_id: int) -> Optional[Producto]:
    return db.query(Producto).filter(Producto.id == producto_id).first()


def get_producto_por_codigo(db: Session, codigo: str) -> Optional[Producto]:
    return db.query(Producto).filter(Producto.codigo == codigo).first()


def get_producto_por_codigo_barras(db: Session, codigo_barras: str) -> Optional[Producto]:
    return db.query(Producto).filter(Producto.codigo_barras == codigo_barras).first()


def crear_producto(db: Session, producto: ProductoCreate) -> Producto:
    db_producto = Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def actualizar_producto(db: Session, producto_id: int, producto: ProductoUpdate) -> Optional[Producto]:
    db_producto = get_producto(db, producto_id)
    if db_producto:
        for key, value in producto.model_dump(exclude_unset=True).items():
            setattr(db_producto, key, value)
        db.commit()
        db.refresh(db_producto)
    return db_producto


def eliminar_producto(db: Session, producto_id: int) -> bool:
    """Eliminación lógica del producto"""
    db_producto = get_producto(db, producto_id)
    if db_producto:
        db_producto.activo = False
        db.commit()
        return True
    return False


def get_productos_bajo_stock(db: Session) -> List[Producto]:
    """Obtiene productos cuyo stock está por debajo del mínimo"""
    from app.models.inventario import Inventario
    from sqlalchemy import func
    
    subquery = db.query(
        Inventario.producto_id,
        func.sum(Inventario.stock_actual).label('total_stock')
    ).group_by(Inventario.producto_id).subquery()
    
    return db.query(Producto).join(
        subquery,
        Producto.id == subquery.c.producto_id
    ).filter(
        Producto.activo == True,
        subquery.c.total_stock < Producto.stock_minimo
    ).all()
