"""
Modelo de Producto - Catálogo de productos (pastas dentales, cepillos, etc.)
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UnidadMedida(str, enum.Enum):
    UNIDAD = "unidad"
    CAJA = "caja"
    DOCENA = "docena"
    PAQUETE = "paquete"
    DISPLAY = "display"


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    codigo_barras = Column(String(50), unique=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    
    # Clasificación
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    
    # Características
    presentacion = Column(String(100))  # Ej: "Tubo 75ml", "Cepillo Mediano"
    contenido = Column(String(50))  # Ej: "75ml", "150g"
    unidad_medida = Column(SQLEnum(UnidadMedida), default=UnidadMedida.UNIDAD)
    
    # Precios
    precio_compra = Column(Float, default=0.0)
    precio_venta = Column(Float, default=0.0)
    precio_mayorista = Column(Float, default=0.0)
    
    # Stock
    stock_minimo = Column(Integer, default=10)
    stock_maximo = Column(Integer, default=1000)
    
    # Estado
    activo = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    marca = relationship("Marca", back_populates="productos")
    inventarios = relationship("Inventario", back_populates="producto")
    detalles_venta = relationship("DetalleVenta", back_populates="producto")
    detalles_compra = relationship("DetalleCompra", back_populates="producto")
    
    def __repr__(self):
        return f"<Producto {self.codigo} - {self.nombre}>"
    
    @property
    def margen_ganancia(self):
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0
