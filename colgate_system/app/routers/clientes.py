"""
Router de Clientes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.usuario import Usuario
from app.models.cliente import TipoCliente
from app.schemas.cliente import (
    ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse
)
from app.services import cliente_service
from app.services.auth import get_usuario_actual, es_vendedor

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("", response_model=ClienteListResponse)
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    busqueda: Optional[str] = None,
    tipo: Optional[TipoCliente] = None,
    distrito: Optional[str] = None,
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar clientes con filtros"""
    clientes, total = cliente_service.get_clientes(
        db,
        skip=skip,
        limit=limit,
        busqueda=busqueda,
        tipo=tipo,
        distrito=distrito,
        solo_activos=solo_activos
    )
    return ClienteListResponse(total=total, items=clientes)


@router.get("/por-zona/{distrito}", response_model=list[ClienteResponse])
async def clientes_por_zona(
    distrito: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar clientes de un distrito específico"""
    return cliente_service.get_clientes_por_zona(db, distrito)


@router.get("/credito-vencido", response_model=list[ClienteResponse])
async def clientes_credito_vencido(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Listar clientes con crédito vencido"""
    return cliente_service.get_clientes_con_credito_vencido(db)


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener cliente por ID"""
    cliente = cliente_service.get_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/codigo/{codigo}", response_model=ClienteResponse)
async def obtener_cliente_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener cliente por código"""
    cliente = cliente_service.get_cliente_por_codigo(db, codigo)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/ruc/{ruc}", response_model=ClienteResponse)
async def obtener_cliente_por_ruc(
    ruc: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtener cliente por RUC"""
    cliente = cliente_service.get_cliente_por_ruc(db, ruc)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("", response_model=ClienteResponse)
async def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Crear nuevo cliente"""
    # Verificar código único
    existente = cliente_service.get_cliente_por_codigo(db, cliente.codigo)
    if existente:
        raise HTTPException(status_code=400, detail="El código de cliente ya existe")
    
    # Verificar RUC único
    if cliente.ruc:
        existente = cliente_service.get_cliente_por_ruc(db, cliente.ruc)
        if existente:
            raise HTTPException(status_code=400, detail="El RUC ya está registrado")
    
    return cliente_service.crear_cliente(db, cliente)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: int,
    cliente: ClienteUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Actualizar cliente"""
    resultado = cliente_service.actualizar_cliente(db, cliente_id, cliente)
    if not resultado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return resultado


@router.delete("/{cliente_id}")
async def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_vendedor)
):
    """Eliminar cliente (eliminación lógica)"""
    if not cliente_service.eliminar_cliente(db, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"mensaje": "Cliente eliminado exitosamente"}
