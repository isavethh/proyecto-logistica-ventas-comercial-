"""
Schemas de Usuario - Validación de datos
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.usuario import RolUsuario


class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    nombres: str
    apellidos: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    rol: RolUsuario = RolUsuario.VENDEDOR


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    id: int
    activo: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    rol: Optional[str] = None
