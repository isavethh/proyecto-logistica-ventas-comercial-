"""
Router de Reportes y Estadísticas
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.producto import Producto
from app.models.cliente import Cliente
from app.models.venta import Venta, DetalleVenta, EstadoVenta
from app.models.inventario import Inventario, MovimientoInventario
from app.models.logistica import Envio
from app.models.usuario import Usuario
from app.services.auth import get_usuario_actual

router = APIRouter(prefix="/reportes", tags=["Reportes y Estadísticas"])


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtiene estadísticas generales para el dashboard"""
    
    # Fecha de hoy y hace 30 días
    hoy = datetime.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)
    
    # Estadísticas generales
    total_productos = db.query(func.count(Producto.id)).filter(Producto.activo == True).scalar()
    total_clientes = db.query(func.count(Cliente.id)).filter(Cliente.activo == True).scalar()
    
    # Ventas del mes
    ventas_mes = db.query(Venta).filter(
        func.date(Venta.fecha_creacion) >= hace_30_dias,
        Venta.estado != EstadoVenta.CANCELADO
    ).all()
    
    total_ventas_mes = len(ventas_mes)
    ingresos_mes = sum(v.total for v in ventas_mes) if ventas_mes else 0
    
    # Ventas de la semana
    ventas_semana = db.query(Venta).filter(
        func.date(Venta.fecha_creacion) >= hace_7_dias,
        Venta.estado != EstadoVenta.CANCELADO
    ).all()
    ingresos_semana = sum(v.total for v in ventas_semana) if ventas_semana else 0
    
    # Productos con bajo stock
    productos_bajo_stock = db.query(Inventario).join(Producto).filter(
        Inventario.cantidad <= Producto.stock_minimo,
        Producto.activo == True
    ).count()
    
    # Envíos pendientes
    envios_pendientes = db.query(func.count(Envio.id)).filter(
        Envio.estado.in_(['pendiente', 'en_ruta'])
    ).scalar()
    
    # Ventas por día (últimos 7 días)
    ventas_por_dia = []
    for i in range(7):
        fecha = hoy - timedelta(days=6-i)
        ventas_dia = db.query(Venta).filter(
            func.date(Venta.fecha_creacion) == fecha,
            Venta.estado != EstadoVenta.CANCELADO
        ).all()
        ventas_por_dia.append({
            "fecha": fecha.strftime("%d/%m"),
            "cantidad": len(ventas_dia),
            "total": sum(v.total for v in ventas_dia) if ventas_dia else 0
        })
    
    # Top 5 productos más vendidos
    top_productos = db.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).join(Venta).filter(
        Venta.estado != EstadoVenta.CANCELADO,
        func.date(Venta.fecha_creacion) >= hace_30_dias
    ).group_by(Producto.id).order_by(desc('total_vendido')).limit(5).all()
    
    # Top 5 clientes
    top_clientes = db.query(
        Cliente.razon_social,
        func.sum(Venta.total).label('total_comprado')
    ).join(Venta).filter(
        Venta.estado != EstadoVenta.CANCELADO,
        func.date(Venta.fecha_creacion) >= hace_30_dias
    ).group_by(Cliente.id).order_by(desc('total_comprado')).limit(5).all()
    
    # Ventas por estado
    ventas_por_estado = db.query(
        Venta.estado,
        func.count(Venta.id).label('cantidad')
    ).filter(
        func.date(Venta.fecha_creacion) >= hace_30_dias
    ).group_by(Venta.estado).all()
    
    return {
        "resumen": {
            "total_productos": total_productos,
            "total_clientes": total_clientes,
            "ventas_mes": total_ventas_mes,
            "ingresos_mes": float(ingresos_mes),
            "ingresos_semana": float(ingresos_semana),
            "productos_bajo_stock": productos_bajo_stock,
            "envios_pendientes": envios_pendientes
        },
        "ventas_por_dia": ventas_por_dia,
        "top_productos": [
            {"nombre": p[0], "cantidad": int(p[1])} for p in top_productos
        ],
        "top_clientes": [
            {"nombre": c[0], "total": float(c[1])} for c in top_clientes
        ],
        "ventas_por_estado": [
            {"estado": v[0].value, "cantidad": v[1]} for v in ventas_por_estado
        ]
    }


@router.get("/ventas/mensual")
async def get_ventas_mensuales(
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtiene ventas agrupadas por mes"""
    if year is None:
        year = datetime.now().year
    
    ventas_por_mes = []
    for mes in range(1, 13):
        ventas = db.query(Venta).filter(
            extract('year', Venta.fecha_creacion) == year,
            extract('month', Venta.fecha_creacion) == mes,
            Venta.estado != EstadoVenta.CANCELADO
        ).all()
        
        ventas_por_mes.append({
            "mes": mes,
            "nombre_mes": [
                "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
            ][mes-1],
            "cantidad": len(ventas),
            "total": sum(v.total for v in ventas) if ventas else 0
        })
    
    return {"year": year, "datos": ventas_por_mes}


@router.get("/inventario/alertas")
async def get_alertas_inventario(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtiene productos con alertas de stock"""
    
    # Productos con stock bajo
    stock_bajo = db.query(Inventario, Producto).join(Producto).filter(
        Inventario.cantidad <= Producto.stock_minimo,
        Inventario.cantidad > 0,
        Producto.activo == True
    ).all()
    
    # Productos sin stock
    sin_stock = db.query(Inventario, Producto).join(Producto).filter(
        Inventario.cantidad == 0,
        Producto.activo == True
    ).all()
    
    # Productos cerca del máximo
    stock_alto = db.query(Inventario, Producto).join(Producto).filter(
        Inventario.cantidad >= Producto.stock_maximo * 0.9,
        Producto.activo == True
    ).all()
    
    return {
        "stock_bajo": [
            {
                "producto": p.nombre,
                "codigo": p.codigo,
                "cantidad": i.cantidad,
                "minimo": p.stock_minimo
            } for i, p in stock_bajo
        ],
        "sin_stock": [
            {
                "producto": p.nombre,
                "codigo": p.codigo
            } for i, p in sin_stock
        ],
        "stock_alto": [
            {
                "producto": p.nombre,
                "codigo": p.codigo,
                "cantidad": i.cantidad,
                "maximo": p.stock_maximo
            } for i, p in stock_alto
        ]
    }


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Obtiene KPIs del negocio"""
    
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
    
    # Ventas mes actual
    ventas_mes_actual = db.query(Venta).filter(
        func.date(Venta.fecha_creacion) >= inicio_mes,
        Venta.estado != EstadoVenta.CANCELADO
    ).all()
    total_mes_actual = sum(v.total for v in ventas_mes_actual) if ventas_mes_actual else 0
    
    # Ventas mes anterior
    ventas_mes_anterior = db.query(Venta).filter(
        func.date(Venta.fecha_creacion) >= mes_anterior,
        func.date(Venta.fecha_creacion) < inicio_mes,
        Venta.estado != EstadoVenta.CANCELADO
    ).all()
    total_mes_anterior = sum(v.total for v in ventas_mes_anterior) if ventas_mes_anterior else 0
    
    # Crecimiento
    if total_mes_anterior > 0:
        crecimiento = ((total_mes_actual - total_mes_anterior) / total_mes_anterior) * 100
    else:
        crecimiento = 100 if total_mes_actual > 0 else 0
    
    # Ticket promedio
    ticket_promedio = total_mes_actual / len(ventas_mes_actual) if ventas_mes_actual else 0
    
    # Clientes nuevos este mes
    clientes_nuevos = db.query(func.count(Cliente.id)).filter(
        func.date(Cliente.fecha_registro) >= inicio_mes
    ).scalar()
    
    # Tasa de conversión (ventas confirmadas / total ventas)
    ventas_confirmadas = db.query(func.count(Venta.id)).filter(
        func.date(Venta.fecha_creacion) >= inicio_mes,
        Venta.estado.in_([EstadoVenta.CONFIRMADO, EstadoVenta.EN_PREPARACION, 
                         EstadoVenta.LISTO_ENVIO, EstadoVenta.EN_RUTA, EstadoVenta.ENTREGADO])
    ).scalar()
    
    total_ventas = db.query(func.count(Venta.id)).filter(
        func.date(Venta.fecha_creacion) >= inicio_mes
    ).scalar()
    
    tasa_conversion = (ventas_confirmadas / total_ventas * 100) if total_ventas > 0 else 0
    
    return {
        "ingresos_mes": float(total_mes_actual),
        "ingresos_mes_anterior": float(total_mes_anterior),
        "crecimiento_porcentaje": round(crecimiento, 1),
        "ticket_promedio": round(float(ticket_promedio), 2),
        "clientes_nuevos": clientes_nuevos,
        "tasa_conversion": round(tasa_conversion, 1),
        "total_ordenes": len(ventas_mes_actual)
    }
