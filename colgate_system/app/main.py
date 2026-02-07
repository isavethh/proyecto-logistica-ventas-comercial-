"""
Sistema de Gestión Empresarial - Colgate
Aplicación Principal FastAPI
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import os

from app.config import settings
from app.database import init_db, engine, Base
from app.routers import auth, productos, clientes, inventario, ventas, logistica


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación"""
    # Startup: Inicializar base de datos
    print("🚀 Iniciando Sistema de Gestión Colgate...")
    init_db()
    print("✅ Base de datos inicializada")
    yield
    # Shutdown
    print("👋 Cerrando aplicación...")


# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Sistema de Gestión Empresarial para Comercialización
    
    ### Módulos disponibles:
    - 🔐 **Autenticación**: Login, registro, gestión de usuarios y roles
    - 📦 **Productos**: Catálogo de productos, categorías y marcas
    - 👥 **Clientes**: Gestión de clientes (minoristas, mayoristas, distribuidores)
    - 📊 **Inventario**: Control de stock, almacenes, movimientos
    - 💰 **Ventas**: Pedidos, facturación, estados de venta
    - 🚚 **Logística**: Envíos, rutas, vehículos, conductores
    
    ### Autenticación
    Usa el endpoint `/api/auth/login` para obtener un token JWT.
    Incluye el token en el header: `Authorization: Bearer <token>`
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para medir tiempo de respuesta
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc) if settings.DEBUG else "Contacte al administrador"
        }
    )


# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(productos.router, prefix="/api")
app.include_router(clientes.router, prefix="/api")
app.include_router(inventario.router, prefix="/api")
app.include_router(ventas.router, prefix="/api")
app.include_router(logistica.router, prefix="/api")

# Servir archivos estáticos del frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# Endpoint raíz - Servir el frontend
@app.get("/")
async def root():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "sistema": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "empresa": settings.COMPANY_NAME,
        "estado": "operativo",
        "documentacion": "/docs"
    }


# Endpoint de salud
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


# Endpoint de información
@app.get("/info")
async def system_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": {
            "name": settings.COMPANY_NAME,
            "ruc": settings.COMPANY_RUC,
            "address": settings.COMPANY_ADDRESS
        },
        "modules": [
            "autenticacion",
            "productos",
            "clientes",
            "inventario",
            "ventas",
            "logistica"
        ]
    }
