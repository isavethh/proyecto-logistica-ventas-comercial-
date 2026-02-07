"""
Router de Autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse,
    Token, UsuarioLogin
)
from app.services.auth import (
    autenticar_usuario, crear_token_acceso, get_password_hash,
    get_usuario_actual, es_admin
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Iniciar sesión y obtener token de acceso"""
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Actualizar último acceso
    usuario.ultimo_acceso = datetime.utcnow()
    db.commit()
    
    # Crear token
    access_token = crear_token_acceso(
        data={"sub": usuario.username, "rol": usuario.rol.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/registro", response_model=UsuarioResponse)
async def registrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(es_admin)
):
    """Registrar nuevo usuario (solo administradores)"""
    # Verificar si username ya existe
    if db.query(Usuario).filter(Usuario.username == usuario.username).first():
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Verificar si email ya existe
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    db_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        hashed_password=get_password_hash(usuario.password),
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        dni=usuario.dni,
        telefono=usuario.telefono,
        rol=usuario.rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


@router.get("/me", response_model=UsuarioResponse)
async def obtener_usuario_actual(usuario: Usuario = Depends(get_usuario_actual)):
    """Obtener información del usuario actual"""
    return usuario


@router.put("/me", response_model=UsuarioResponse)
async def actualizar_mi_perfil(
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Actualizar perfil del usuario actual"""
    # No permitir cambiar el rol a sí mismo
    if datos.rol and datos.rol != usuario.rol:
        raise HTTPException(
            status_code=403,
            detail="No puedes cambiar tu propio rol"
        )
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        if key != "rol":  # Excluir rol
            setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/cambiar-password")
async def cambiar_password(
    password_actual: str,
    password_nuevo: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Cambiar contraseña del usuario actual"""
    from app.services.auth import verificar_password
    
    if not verificar_password(password_actual, usuario.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Contraseña actual incorrecta"
        )
    
    usuario.hashed_password = get_password_hash(password_nuevo)
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente"}


# ============ GESTIÓN DE USUARIOS (ADMIN) ============
@router.get("/usuarios", response_model=list[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(es_admin)
):
    """Listar todos los usuarios (solo admin)"""
    query = db.query(Usuario)
    if activo is not None:
        query = query.filter(Usuario.activo == activo)
    return query.offset(skip).limit(limit).all()


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(es_admin)
):
    """Obtener usuario por ID (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(es_admin)
):
    """Actualizar usuario (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/usuarios/{usuario_id}")
async def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(es_admin)
):
    """Desactivar usuario (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario.id == admin.id:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo")
    
    usuario.activo = False
    db.commit()
    
    return {"mensaje": "Usuario desactivado exitosamente"}
