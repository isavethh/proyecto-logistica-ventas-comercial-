# Sistema de Gestión Empresarial - Colgate

## 📋 Descripción
Sistema completo de gestión empresarial para comercialización de productos de higiene bucal (tipo Colgate). Incluye módulos de ventas, inventario, logística, clientes y más..

## 🚀 Tecnologías Utilizadas

### Backend
- **Python 3.10+** - Lenguaje de programación
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos (fácil migrar a PostgreSQL)
- **Pydantic** - Validación de datos
- **JWT** - Autenticación con tokens

### Frontend
- **HTML5 / CSS3 / JavaScript**
- **Bootstrap 5** - Framework CSS
- **Bootstrap Icons** - Iconos

## 📦 Módulos del Sistema

### 1. 🔐 Autenticación y Usuarios
- Login con JWT
- Roles: Admin, Gerente, Vendedor, Almacenero, Logística, Contador
- Gestión de usuarios

### 2. 📦 Productos
- Catálogo de productos
- Categorías y Marcas
- Precios: compra, venta, mayorista
- Stock mínimo/máximo

### 3. 👥 Clientes
- Tipos: Minorista, Mayorista, Distribuidor, Cadena
- Datos de contacto y dirección
- Condiciones comerciales (crédito, descuentos)
- Coordenadas para logística

### 4. 🏭 Proveedores
- Gestión de proveedores
- Órdenes de compra
- Control de entregas

### 5. 📊 Inventario
- Múltiples almacenes
- Control de stock por ubicación
- Movimientos (entradas, salidas, transferencias)
- Alertas de stock bajo
- Control de lotes y vencimientos

### 6. 💰 Ventas
- Pedidos con múltiples estados
- Facturación (Factura, Boleta, Nota de Venta)
- Tipos de pago (Contado, Crédito, Transferencia)
- Cálculo automático de IGV (18%)
- Seguimiento de entregas

### 7. 🚚 Logística
- Gestión de vehículos
- Gestión de conductores
- Zonas de reparto
- Rutas de distribución
- Seguimiento de envíos
- Dashboard de logística

## 🛠️ Instalación

### 1. Clonar o descargar el proyecto
```bash
cd colgate_system
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el sistema
```bash
python run.py
```

El servidor iniciará en: **http://localhost:8000**

## 📖 Documentación API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 👤 Usuarios de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Administrador |
| gerente | gerente123 | Gerente |
| vendedor1 | vendedor123 | Vendedor |
| almacenero1 | almacen123 | Almacenero |
| logistica1 | logistica123 | Logística |

## 🌐 Frontend Web

Abrir en el navegador:
```
frontend/index.html
```

O servir con un servidor web local.

## 📁 Estructura del Proyecto

```
colgate_system/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuración
│   ├── database.py         # Conexión DB
│   ├── main.py             # App FastAPI
│   ├── seed_data.py        # Datos de ejemplo
│   │
│   ├── models/             # Modelos SQLAlchemy
│   │   ├── usuario.py
│   │   ├── producto.py
│   │   ├── categoria.py
│   │   ├── cliente.py
│   │   ├── proveedor.py
│   │   ├── inventario.py
│   │   ├── venta.py
│   │   └── logistica.py
│   │
│   ├── schemas/            # Schemas Pydantic
│   │   ├── usuario.py
│   │   ├── producto.py
│   │   ├── cliente.py
│   │   ├── proveedor.py
│   │   ├── inventario.py
│   │   ├── venta.py
│   │   └── logistica.py
│   │
│   ├── services/           # Lógica de negocio
│   │   ├── auth.py
│   │   ├── producto_service.py
│   │   ├── cliente_service.py
│   │   ├── inventario_service.py
│   │   ├── venta_service.py
│   │   └── logistica_service.py
│   │
│   └── routers/            # Endpoints API
│       ├── auth.py
│       ├── productos.py
│       ├── clientes.py
│       ├── inventario.py
│       ├── ventas.py
│       └── logistica.py
│
├── frontend/
│   ├── index.html
│   └── app.js
│
├── requirements.txt
├── run.py
└── README.md
```

## 🔧 Configuración

Las variables de configuración están en `app/config.py`:

```python
APP_NAME = "Sistema de Gestión Colgate"
DATABASE_URL = "sqlite:///./colgate_system.db"
SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas
```

## 📈 Endpoints Principales

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Usuario actual
- `POST /api/auth/registro` - Registrar usuario (admin)

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `GET /api/productos/{id}` - Obtener producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Eliminar producto

### Clientes
- `GET /api/clientes` - Listar clientes
- `POST /api/clientes` - Crear cliente
- `GET /api/clientes/{id}` - Obtener cliente
- `PUT /api/clientes/{id}` - Actualizar cliente

### Inventario
- `GET /api/inventario/almacenes` - Listar almacenes
- `GET /api/inventario/producto/{id}` - Stock de producto
- `POST /api/inventario/ajuste` - Ajuste de inventario
- `POST /api/inventario/transferencia` - Transferencia

### Ventas
- `GET /api/ventas` - Listar ventas
- `POST /api/ventas` - Crear venta
- `POST /api/ventas/{id}/confirmar` - Confirmar venta
- `POST /api/ventas/{id}/cancelar` - Cancelar venta

### Logística
- `GET /api/logistica/dashboard` - Dashboard
- `GET /api/logistica/envios` - Listar envíos
- `POST /api/logistica/envios/venta/{id}` - Crear envío
- `POST /api/logistica/envios/{id}/completar` - Completar envío

## 🎓 Uso para Tesis

Este sistema es ideal para una tesis de grado porque:

1. **Arquitectura moderna**: Usa patrones de diseño actuales (MVC, Repository, Services)
2. **API RESTful**: Documentación automática con OpenAPI/Swagger
3. **Escalable**: Fácil de migrar a PostgreSQL y desplegar en la nube
4. **Seguridad**: Autenticación JWT con roles y permisos
5. **Completo**: Cubre múltiples módulos de un ERP real

## 📝 Licencia

Este proyecto es para fines educativos.

---

Desarrollado con ❤️ para tu tesis
