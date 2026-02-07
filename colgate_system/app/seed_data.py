"""
Script para inicializar datos de ejemplo
"""
from app.database import SessionLocal, init_db
from app.models.usuario import Usuario, RolUsuario
from app.models.categoria import Categoria, Marca
from app.models.producto import Producto, UnidadMedida
from app.models.cliente import Cliente, TipoCliente
from app.models.proveedor import Proveedor, TipoProveedor
from app.models.inventario import Almacen, Inventario, TipoAlmacen
from app.models.logistica import Vehiculo, Conductor, ZonaReparto, TipoVehiculo
from app.services.auth import get_password_hash


def crear_datos_ejemplo():
    """Crea datos de ejemplo para el sistema"""
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Usuario).first():
            print("⚠️  Ya existen datos en la base de datos")
            return
        
        print("📦 Creando datos de ejemplo...")
        
        # ============ USUARIOS ============
        usuarios = [
            Usuario(
                username="admin",
                email="admin@colgate.com",
                hashed_password=get_password_hash("admin123"),
                nombres="Administrador",
                apellidos="Sistema",
                dni="00000001",
                rol=RolUsuario.ADMIN,
                activo=True
            ),
            Usuario(
                username="gerente",
                email="gerente@colgate.com",
                hashed_password=get_password_hash("gerente123"),
                nombres="Carlos",
                apellidos="Mendoza",
                dni="12345678",
                rol=RolUsuario.GERENTE,
                activo=True
            ),
            Usuario(
                username="vendedor1",
                email="vendedor1@colgate.com",
                hashed_password=get_password_hash("vendedor123"),
                nombres="María",
                apellidos="García",
                dni="23456789",
                telefono="987654321",
                rol=RolUsuario.VENDEDOR,
                activo=True
            ),
            Usuario(
                username="almacenero1",
                email="almacen@colgate.com",
                hashed_password=get_password_hash("almacen123"),
                nombres="José",
                apellidos="López",
                dni="34567890",
                rol=RolUsuario.ALMACENERO,
                activo=True
            ),
            Usuario(
                username="logistica1",
                email="logistica@colgate.com",
                hashed_password=get_password_hash("logistica123"),
                nombres="Ana",
                apellidos="Martínez",
                dni="45678901",
                rol=RolUsuario.LOGISTICA,
                activo=True
            ),
        ]
        db.add_all(usuarios)
        
        # ============ CATEGORÍAS ============
        categorias = [
            Categoria(codigo="CAT001", nombre="Pastas Dentales", descripcion="Cremas y pastas dentales"),
            Categoria(codigo="CAT002", nombre="Cepillos Dentales", descripcion="Cepillos manuales y eléctricos"),
            Categoria(codigo="CAT003", nombre="Enjuagues Bucales", descripcion="Enjuagues y colutorios"),
            Categoria(codigo="CAT004", nombre="Hilo Dental", descripcion="Hilos y sedas dentales"),
            Categoria(codigo="CAT005", nombre="Blanqueadores", descripcion="Productos de blanqueamiento"),
        ]
        db.add_all(categorias)
        
        # ============ MARCAS ============
        marcas = [
            Marca(codigo="MRC001", nombre="Colgate", descripcion="Marca principal", pais_origen="USA"),
            Marca(codigo="MRC002", nombre="Colgate Total", descripcion="Línea Total", pais_origen="USA"),
            Marca(codigo="MRC003", nombre="Colgate Sensitive", descripcion="Línea para sensibilidad", pais_origen="USA"),
            Marca(codigo="MRC004", nombre="Colgate Kids", descripcion="Línea infantil", pais_origen="USA"),
            Marca(codigo="MRC005", nombre="Colgate Luminous White", descripcion="Línea blanqueadora", pais_origen="USA"),
        ]
        db.add_all(marcas)
        db.flush()
        
        # ============ PRODUCTOS ============
        productos = [
            # Pastas dentales
            Producto(
                codigo="PRD001", codigo_barras="7891024132135",
                nombre="Colgate Triple Acción 75ml",
                descripcion="Pasta dental con triple protección",
                categoria_id=1, marca_id=1,
                presentacion="Tubo 75ml", contenido="75ml",
                precio_compra=2.50, precio_venta=4.50, precio_mayorista=3.80,
                stock_minimo=50, stock_maximo=500
            ),
            Producto(
                codigo="PRD002", codigo_barras="7891024132136",
                nombre="Colgate Triple Acción 150ml",
                descripcion="Pasta dental con triple protección - grande",
                categoria_id=1, marca_id=1,
                presentacion="Tubo 150ml", contenido="150ml",
                precio_compra=4.00, precio_venta=7.50, precio_mayorista=6.50,
                stock_minimo=30, stock_maximo=300
            ),
            Producto(
                codigo="PRD003", codigo_barras="7891024132137",
                nombre="Colgate Total 12 90g",
                descripcion="Protección completa 12 horas",
                categoria_id=1, marca_id=2,
                presentacion="Tubo 90g", contenido="90g",
                precio_compra=5.50, precio_venta=9.90, precio_mayorista=8.50,
                stock_minimo=40, stock_maximo=400
            ),
            Producto(
                codigo="PRD004", codigo_barras="7891024132138",
                nombre="Colgate Sensitive Pro-Alivio 75ml",
                descripcion="Alivio instantáneo para dientes sensibles",
                categoria_id=1, marca_id=3,
                presentacion="Tubo 75ml", contenido="75ml",
                precio_compra=6.00, precio_venta=11.50, precio_mayorista=9.80,
                stock_minimo=25, stock_maximo=250
            ),
            Producto(
                codigo="PRD005", codigo_barras="7891024132139",
                nombre="Colgate Kids Minions 75ml",
                descripcion="Pasta dental para niños sabor fresa",
                categoria_id=1, marca_id=4,
                presentacion="Tubo 75ml", contenido="75ml",
                precio_compra=3.00, precio_venta=5.90, precio_mayorista=4.80,
                stock_minimo=30, stock_maximo=300
            ),
            # Cepillos
            Producto(
                codigo="PRD006", codigo_barras="7891024132140",
                nombre="Cepillo Colgate Premier Clean Medio",
                descripcion="Cepillo dental con cerdas medianas",
                categoria_id=2, marca_id=1,
                presentacion="Unidad", contenido="1 unidad",
                precio_compra=1.50, precio_venta=3.50, precio_mayorista=2.80,
                stock_minimo=100, stock_maximo=1000
            ),
            Producto(
                codigo="PRD007", codigo_barras="7891024132141",
                nombre="Cepillo Colgate 360° Suave",
                descripcion="Limpieza completa 360 grados",
                categoria_id=2, marca_id=1,
                presentacion="Unidad", contenido="1 unidad",
                precio_compra=4.00, precio_venta=8.50, precio_mayorista=7.00,
                stock_minimo=50, stock_maximo=500
            ),
            Producto(
                codigo="PRD008", codigo_barras="7891024132142",
                nombre="Cepillo Colgate Kids Minions",
                descripcion="Cepillo infantil extra suave",
                categoria_id=2, marca_id=4,
                presentacion="Unidad", contenido="1 unidad",
                precio_compra=2.00, precio_venta=4.90, precio_mayorista=3.90,
                stock_minimo=60, stock_maximo=600
            ),
            # Enjuagues
            Producto(
                codigo="PRD009", codigo_barras="7891024132143",
                nombre="Enjuague Colgate Plax Menta 250ml",
                descripcion="Enjuague bucal sabor menta fresca",
                categoria_id=3, marca_id=1,
                presentacion="Botella 250ml", contenido="250ml",
                precio_compra=5.00, precio_venta=9.90, precio_mayorista=8.20,
                stock_minimo=40, stock_maximo=400
            ),
            Producto(
                codigo="PRD010", codigo_barras="7891024132144",
                nombre="Enjuague Colgate Plax Menta 500ml",
                descripcion="Enjuague bucal sabor menta fresca - grande",
                categoria_id=3, marca_id=1,
                presentacion="Botella 500ml", contenido="500ml",
                precio_compra=8.00, precio_venta=15.90, precio_mayorista=13.50,
                stock_minimo=25, stock_maximo=250
            ),
            # Hilo dental
            Producto(
                codigo="PRD011", codigo_barras="7891024132145",
                nombre="Hilo Dental Colgate Total 25m",
                descripcion="Hilo dental con cera",
                categoria_id=4, marca_id=2,
                presentacion="Carrete 25m", contenido="25m",
                precio_compra=3.50, precio_venta=7.50, precio_mayorista=6.00,
                stock_minimo=50, stock_maximo=500
            ),
            # Blanqueadores
            Producto(
                codigo="PRD012", codigo_barras="7891024132146",
                nombre="Colgate Luminous White 75ml",
                descripcion="Pasta blanqueadora instantánea",
                categoria_id=5, marca_id=5,
                presentacion="Tubo 75ml", contenido="75ml",
                precio_compra=7.00, precio_venta=13.90, precio_mayorista=11.50,
                stock_minimo=30, stock_maximo=300
            ),
        ]
        db.add_all(productos)
        
        # ============ CLIENTES ============
        clientes = [
            Cliente(
                codigo="CLI001", razon_social="Farmacia San José SAC",
                nombre_comercial="Farmacia San José", ruc="20123456789",
                tipo=TipoCliente.MINORISTA,
                contacto_nombre="Juan Pérez", contacto_telefono="01-234-5678",
                contacto_email="ventas@farmaciasanjose.com",
                direccion="Av. Arequipa 1234", distrito="Lince",
                provincia="Lima", departamento="Lima",
                limite_credito=5000.00, dias_credito=30
            ),
            Cliente(
                codigo="CLI002", razon_social="Distribuidora Norte SAC",
                nombre_comercial="Dist. Norte", ruc="20234567890",
                tipo=TipoCliente.MAYORISTA,
                contacto_nombre="Pedro Sánchez", contacto_telefono="01-345-6789",
                contacto_email="compras@distnorte.com",
                direccion="Jr. Industrial 567", distrito="Los Olivos",
                provincia="Lima", departamento="Lima",
                limite_credito=25000.00, dias_credito=45,
                descuento_especial=5.0
            ),
            Cliente(
                codigo="CLI003", razon_social="Supermercados Metro SA",
                nombre_comercial="Metro", ruc="20345678901",
                tipo=TipoCliente.CADENA,
                contacto_nombre="Laura Torres", contacto_telefono="01-456-7890",
                contacto_email="proveedores@metro.pe",
                direccion="Av. La Marina 2500", distrito="San Miguel",
                provincia="Lima", departamento="Lima",
                limite_credito=100000.00, dias_credito=60,
                descuento_especial=10.0
            ),
            Cliente(
                codigo="CLI004", razon_social="Bodega Doña Rosa",
                nombre_comercial="Bodega Rosa", ruc="10456789012",
                tipo=TipoCliente.MINORISTA,
                contacto_nombre="Rosa Mendoza", contacto_telefono="999-888-777",
                direccion="Calle Los Pinos 123", distrito="Surquillo",
                provincia="Lima", departamento="Lima",
                limite_credito=1000.00, dias_credito=7
            ),
            Cliente(
                codigo="CLI005", razon_social="Comercial Wong SA",
                nombre_comercial="Wong", ruc="20567890123",
                tipo=TipoCliente.CADENA,
                contacto_nombre="Carlos Vega", contacto_telefono="01-567-8901",
                contacto_email="compras@wong.pe",
                direccion="Av. Dos de Mayo 1099", distrito="Miraflores",
                provincia="Lima", departamento="Lima",
                limite_credito=150000.00, dias_credito=60,
                descuento_especial=12.0
            ),
        ]
        db.add_all(clientes)
        
        # ============ PROVEEDORES ============
        proveedores = [
            Proveedor(
                codigo="PROV001", razon_social="Colgate-Palmolive Perú SA",
                nombre_comercial="Colgate Perú", ruc="20100047218",
                tipo=TipoProveedor.FABRICANTE,
                contacto_nombre="Roberto Fernández", contacto_telefono="01-611-0000",
                contacto_email="ventas@colgate.com.pe",
                direccion="Av. República de Panamá 3420", ciudad="Lima",
                dias_entrega=5, dias_credito=45
            ),
            Proveedor(
                codigo="PROV002", razon_social="Distribuidora Central SAC",
                nombre_comercial="DisCentral", ruc="20678901234",
                tipo=TipoProveedor.DISTRIBUIDOR,
                contacto_nombre="Miguel Ruiz", contacto_telefono="01-789-0123",
                contacto_email="pedidos@discentral.com",
                direccion="Jr. Comercio 890", ciudad="Lima",
                dias_entrega=3, dias_credito=30
            ),
        ]
        db.add_all(proveedores)
        
        # ============ ALMACENES ============
        almacenes = [
            Almacen(
                codigo="ALM001", nombre="Almacén Principal",
                tipo=TipoAlmacen.PRINCIPAL,
                direccion="Av. Argentina 1234", distrito="Callao",
                ciudad="Lima",
                responsable="José López", telefono="01-890-1234"
            ),
            Almacen(
                codigo="ALM002", nombre="Almacén Norte",
                tipo=TipoAlmacen.SECUNDARIO,
                direccion="Av. Túpac Amaru 5678", distrito="Comas",
                ciudad="Lima",
                responsable="María Santos", telefono="01-901-2345"
            ),
        ]
        db.add_all(almacenes)
        db.flush()
        
        # ============ INVENTARIO INICIAL ============
        # Agregar stock a almacén principal
        for i, producto in enumerate(productos):
            inventario = Inventario(
                producto_id=producto.id,
                almacen_id=1,  # Almacén principal
                stock_actual=100 * (i + 1),
                stock_reservado=0,
                stock_disponible=100 * (i + 1),
                ubicacion=f"A-{(i//4)+1:02d}-{(i%4)+1:02d}"
            )
            db.add(inventario)
        
        # ============ VEHÍCULOS ============
        vehiculos = [
            Vehiculo(
                codigo="VEH001", placa="ABC-123",
                tipo=TipoVehiculo.FURGONETA,
                marca="Mercedes-Benz", modelo="Sprinter", anio=2022,
                capacidad_peso=1500, capacidad_volumen=12
            ),
            Vehiculo(
                codigo="VEH002", placa="DEF-456",
                tipo=TipoVehiculo.CAMION_PEQUENO,
                marca="Hyundai", modelo="HD65", anio=2021,
                capacidad_peso=3000, capacidad_volumen=20
            ),
            Vehiculo(
                codigo="VEH003", placa="GHI-789",
                tipo=TipoVehiculo.MOTO,
                marca="Honda", modelo="Wave 110", anio=2023,
                capacidad_peso=50, capacidad_volumen=0.5
            ),
        ]
        db.add_all(vehiculos)
        
        # ============ CONDUCTORES ============
        conductores = [
            Conductor(
                codigo="CON001", nombres="Luis", apellidos="Ramírez",
                dni="56789012", telefono="999-111-222",
                licencia_numero="Q56789012", licencia_categoria="A-IIb"
            ),
            Conductor(
                codigo="CON002", nombres="Jorge", apellidos="Castillo",
                dni="67890123", telefono="999-222-333",
                licencia_numero="Q67890123", licencia_categoria="A-IIb"
            ),
            Conductor(
                codigo="CON003", nombres="Diego", apellidos="Vargas",
                dni="78901234", telefono="999-333-444",
                licencia_numero="Q78901234", licencia_categoria="A-I"
            ),
        ]
        db.add_all(conductores)
        
        # ============ ZONAS DE REPARTO ============
        zonas = [
            ZonaReparto(
                codigo="ZON001", nombre="Lima Centro",
                distritos="Cercado,Breña,La Victoria,Lince,Jesús María",
                dias_reparto="lunes,miercoles,viernes"
            ),
            ZonaReparto(
                codigo="ZON002", nombre="Lima Norte",
                distritos="Los Olivos,Independencia,Comas,San Martín de Porres",
                dias_reparto="martes,jueves"
            ),
            ZonaReparto(
                codigo="ZON003", nombre="Lima Sur",
                distritos="Surquillo,Miraflores,San Isidro,Barranco,Chorrillos",
                dias_reparto="lunes,miercoles,viernes"
            ),
        ]
        db.add_all(zonas)
        
        db.commit()
        print("✅ Datos de ejemplo creados exitosamente")
        print("\n📋 Usuarios creados:")
        print("   - admin / admin123 (Administrador)")
        print("   - gerente / gerente123 (Gerente)")
        print("   - vendedor1 / vendedor123 (Vendedor)")
        print("   - almacenero1 / almacen123 (Almacenero)")
        print("   - logistica1 / logistica123 (Logística)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    crear_datos_ejemplo()
