"""
Router de Productos, Categorías y Marcas
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.producto import (
    ProductoCreate, ProductoUpdate, ProductoResponse, ProductoListResponse,
    CategoriaCreate, CategoriaUpdate, CategoriaResponse,
    MarcaCreate, MarcaUpdate, MarcaResponse
)
from app.services import producto_service
from app.services.auth import get_usuario_actual, es_gerente_o_admin

router = APIRouter(prefix="/productos", tags=["Productos"])


# ============ CATEGORÍAS ============
@router.get("/categorias", response_model=list[CategoriaResponse])
async def listar_categorias(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar todas las categorías"""
    return producto_service.get_categorias(db, solo_activos=solo_activos)


@router.post("/categorias", response_model=CategoriaResponse)
async def crear_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Crear nueva categoría"""
    existente = producto_service.get_categoria_por_codigo(db, categoria.codigo)
    if existente:
        raise HTTPException(status_code=400, detail="El código de categoría ya existe")
    return producto_service.crear_categoria(db, categoria)


@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
async def actualizar_categoria(
    categoria_id: int,
    categoria: CategoriaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Actualizar categoría"""
    resultado = producto_service.actualizar_categoria(db, categoria_id, categoria)
    if not resultado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return resultado


# ============ MARCAS ============
@router.get("/marcas", response_model=list[MarcaResponse])
async def listar_marcas(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar todas las marcas"""
    return producto_service.get_marcas(db, solo_activos=solo_activos)


@router.post("/marcas", response_model=MarcaResponse)
async def crear_marca(
    marca: MarcaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Crear nueva marca"""
    return producto_service.crear_marca(db, marca)


@router.put("/marcas/{marca_id}", response_model=MarcaResponse)
async def actualizar_marca(
    marca_id: int,
    marca: MarcaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Actualizar marca"""
    resultado = producto_service.actualizar_marca(db, marca_id, marca)
    if not resultado:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return resultado


# ============ PRODUCTOS ============
@router.get("", response_model=ProductoListResponse)
async def listar_productos(
    skip: int = 0,
    limit: int = 100,
    busqueda: Optional[str] = None,
    categoria_id: Optional[int] = None,
    marca_id: Optional[int] = None,
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar productos con filtros"""
    productos, total = producto_service.get_productos(
        db,
        skip=skip,
        limit=limit,
        busqueda=busqueda,
        categoria_id=categoria_id,
        marca_id=marca_id,
        solo_activos=solo_activos
    )
    return ProductoListResponse(total=total, items=productos)


@router.get("/bajo-stock", response_model=list[ProductoResponse])
async def productos_bajo_stock(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar productos con stock bajo el mínimo"""
    return producto_service.get_productos_bajo_stock(db)


@router.get("/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener producto por ID"""
    producto = producto_service.get_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo/{codigo}", response_model=ProductoResponse)
async def obtener_producto_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener producto por código"""
    producto = producto_service.get_producto_por_codigo(db, codigo)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/barras/{codigo_barras}", response_model=ProductoResponse)
async def obtener_producto_por_barras(
    codigo_barras: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener producto por código de barras"""
    producto = producto_service.get_producto_por_codigo_barras(db, codigo_barras)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("", response_model=ProductoResponse)
async def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Crear nuevo producto"""
    # Verificar código único
    existente = producto_service.get_producto_por_codigo(db, producto.codigo)
    if existente:
        raise HTTPException(status_code=400, detail="El código de producto ya existe")
    
    # Verificar código de barras único
    if producto.codigo_barras:
        existente = producto_service.get_producto_por_codigo_barras(db, producto.codigo_barras)
        if existente:
            raise HTTPException(status_code=400, detail="El código de barras ya existe")
    
    return producto_service.crear_producto(db, producto)


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Actualizar producto"""
    resultado = producto_service.actualizar_producto(db, producto_id, producto)
    if not resultado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return resultado


@router.delete("/{producto_id}")
async def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_gerente_o_admin)
):
    """Eliminar producto (eliminación lógica)"""
    if not producto_service.eliminar_producto(db, producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado exitosamente"}
