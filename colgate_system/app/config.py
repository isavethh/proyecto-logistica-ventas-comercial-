"""
Configuración general del sistema
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "Sistema de Gestión Colgate"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./colgate_system.db"
    
    # Seguridad
    SECRET_KEY: str = "tu_clave_secreta_super_segura_cambiar_en_produccion_2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Configuración de empresa
    COMPANY_NAME: str = "Colgate-Palmolive"
    COMPANY_RUC: str = "20100047218"
    COMPANY_ADDRESS: str = "Av. Industrial 123, Lima, Perú"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
