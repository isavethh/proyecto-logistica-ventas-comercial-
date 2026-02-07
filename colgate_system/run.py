"""
Script principal para ejecutar el servidor
"""
import uvicorn
from app.database import init_db
from app.seed_data import crear_datos_ejemplo


def main():
    # Inicializar base de datos
    print("🔧 Inicializando base de datos...")
    init_db()
    
    # Crear datos de ejemplo
    print("📦 Verificando datos de ejemplo...")
    crear_datos_ejemplo()
    
    # Iniciar servidor
    print("\n🚀 Iniciando servidor...")
    print("📖 Documentación disponible en: http://localhost:8000/docs")
    print("📖 Documentación alternativa: http://localhost:8000/redoc")
    print("\n⏹️  Presiona Ctrl+C para detener el servidor\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
