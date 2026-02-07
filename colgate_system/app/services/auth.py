"""
Servicio de Autenticación y Seguridad
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.schemas.usuario import TokenData

# Configuración de password hashing - compatible con nuevas versiones de bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verifica si el password coincide con el hash"""
    return pwd_context.verify(password_plano, password_hash)


def get_password_hash(password: str) -> str:
    """Genera hash del password"""
    return pwd_context.hash(password)


def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def autenticar_usuario(db: Session, username: str, password: str) -> Optional[Usuario]:
    """Autentica un usuario por username y password"""
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if not usuario:
        return None
    if not verificar_password(password, usuario.hashed_password):
        return None
    if not usuario.activo:
        return None
    return usuario


async def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, rol=payload.get("rol"))
    except JWTError:
        raise credentials_exception
    
    usuario = db.query(Usuario).filter(Usuario.username == token_data.username).first()
    if usuario is None:
        raise credentials_exception
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    return usuario


def get_usuario_activo(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """Verifica que el usuario esté activo"""
    if not usuario.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return usuario


def requiere_rol(*roles_permitidos: RolUsuario):
    """Decorator para requerir roles específicos"""
    def verificar_rol(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para esta acción. Roles permitidos: {[r.value for r in roles_permitidos]}"
            )
        return usuario
    return verificar_rol


# Dependencias de rol comunes
es_admin = requiere_rol(RolUsuario.ADMIN)
es_gerente_o_admin = requiere_rol(RolUsuario.ADMIN, RolUsuario.GERENTE)
es_vendedor = requiere_rol(RolUsuario.ADMIN, RolUsuario.GERENTE, RolUsuario.VENDEDOR)
es_almacenero = requiere_rol(RolUsuario.ADMIN, RolUsuario.GERENTE, RolUsuario.ALMACENERO)
es_logistica = requiere_rol(RolUsuario.ADMIN, RolUsuario.GERENTE, RolUsuario.LOGISTICA)
