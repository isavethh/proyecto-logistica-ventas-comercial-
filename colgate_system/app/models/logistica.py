"""
Modelo de Logística - Gestión de envíos, rutas y distribución
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Time
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class EstadoEnvio(str, enum.Enum):
    PENDIENTE = "pendiente"
    ASIGNADO = "asignado"
    EN_CARGA = "en_carga"
    EN_RUTA = "en_ruta"
    ENTREGADO = "entregado"
    ENTREGA_PARCIAL = "entrega_parcial"
    NO_ENTREGADO = "no_entregado"
    REPROGRAMADO = "reprogramado"


class TipoVehiculo(str, enum.Enum):
    MOTO = "moto"
    FURGONETA = "furgoneta"
    CAMION_PEQUENO = "camion_pequeno"
    CAMION_GRANDE = "camion_grande"


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    placa = Column(String(20), unique=True, nullable=False)
    
    # Características
    tipo = Column(SQLEnum(TipoVehiculo), default=TipoVehiculo.FURGONETA)
    marca = Column(String(50))
    modelo = Column(String(50))
    anio = Column(Integer)
    
    # Capacidad
    capacidad_peso = Column(Float)  # en kg
    capacidad_volumen = Column(Float)  # en m3
    
    # Estado
    activo = Column(Boolean, default=True)
    disponible = Column(Boolean, default=True)
    
    # Documentos
    soat_vencimiento = Column(DateTime)
    revision_tecnica_vencimiento = Column(DateTime)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    envios = relationship("Envio", back_populates="vehiculo")
    
    def __repr__(self):
        return f"<Vehiculo {self.placa} - {self.tipo}>"


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    
    # Datos personales
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(20))
    
    # Licencia
    licencia_numero = Column(String(20))
    licencia_categoria = Column(String(10))
    licencia_vencimiento = Column(DateTime)
    
    # Estado
    activo = Column(Boolean, default=True)
    disponible = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    envios = relationship("Envio", back_populates="conductor")
    
    def __repr__(self):
        return f"<Conductor {self.dni} - {self.nombres} {self.apellidos}>"


class ZonaReparto(Base):
    __tablename__ = "zonas_reparto"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    
    # Área geográfica
    distritos = Column(Text)  # Lista de distritos separados por coma
    descripcion = Column(Text)
    
    # Configuración
    dias_reparto = Column(String(50))  # Ej: "lunes,miercoles,viernes"
    hora_inicio = Column(Time)
    hora_fin = Column(Time)
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    rutas = relationship("RutaReparto", back_populates="zona")
    
    def __repr__(self):
        return f"<ZonaReparto {self.codigo} - {self.nombre}>"


class RutaReparto(Base):
    __tablename__ = "rutas_reparto"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    
    # Zona
    zona_id = Column(Integer, ForeignKey("zonas_reparto.id"))
    
    # Programación
    fecha = Column(DateTime, nullable=False)
    hora_salida_programada = Column(Time)
    hora_salida_real = Column(Time)
    hora_retorno = Column(Time)
    
    # Asignación
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    conductor_id = Column(Integer, ForeignKey("conductores.id"))
    
    # Métricas
    total_entregas = Column(Integer, default=0)
    entregas_exitosas = Column(Integer, default=0)
    entregas_fallidas = Column(Integer, default=0)
    kilometros_recorridos = Column(Float, default=0.0)
    
    # Estado
    completada = Column(Boolean, default=False)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    zona = relationship("ZonaReparto", back_populates="rutas")
    vehiculo = relationship("Vehiculo")
    conductor = relationship("Conductor")
    envios = relationship("Envio", back_populates="ruta")
    
    def __repr__(self):
        return f"<RutaReparto {self.codigo} - {self.fecha}>"


class Envio(Base):
    __tablename__ = "envios"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    
    # Venta asociada
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    
    # Ruta asignada
    ruta_id = Column(Integer, ForeignKey("rutas_reparto.id"))
    
    # Asignación directa (si no hay ruta)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    conductor_id = Column(Integer, ForeignKey("conductores.id"))
    
    # Orden en la ruta
    orden_entrega = Column(Integer)
    
    # Estado
    estado = Column(SQLEnum(EstadoEnvio), default=EstadoEnvio.PENDIENTE)
    
    # Programación
    fecha_programada = Column(DateTime)
    hora_estimada_llegada = Column(Time)
    
    # Entrega
    fecha_entrega = Column(DateTime)
    firma_recibido = Column(Boolean, default=False)
    nombre_recibio = Column(String(100))
    dni_recibio = Column(String(20))
    
    # Observaciones
    observaciones = Column(Text)
    motivo_no_entrega = Column(Text)
    
    # Ubicación de entrega registrada
    latitud_entrega = Column(Float)
    longitud_entrega = Column(Float)
    
    # Auditoría
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    venta = relationship("Venta", back_populates="envio")
    ruta = relationship("RutaReparto", back_populates="envios")
    vehiculo = relationship("Vehiculo", back_populates="envios")
    conductor = relationship("Conductor", back_populates="envios")
    
    def __repr__(self):
        return f"<Envio {self.codigo} - {self.estado}>"


class RutaCliente(Base):
    """Asociación entre clientes y zonas de reparto para rutas frecuentes"""
    __tablename__ = "rutas_clientes"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    zona_id = Column(Integer, ForeignKey("zonas_reparto.id"))
    
    # Día preferido de visita
    dia_visita = Column(String(20))  # lunes, martes, etc.
    frecuencia = Column(String(20))  # semanal, quincenal, mensual
    
    # Ventana de tiempo preferida
    hora_preferida_inicio = Column(Time)
    hora_preferida_fin = Column(Time)
    
    # Notas
    instrucciones_entrega = Column(Text)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="rutas")
    
    def __repr__(self):
        return f"<RutaCliente {self.cliente_id} - {self.dia_visita}>"
