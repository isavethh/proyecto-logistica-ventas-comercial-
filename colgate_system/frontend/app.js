/**
 * Sistema de Gestión Colgate - Frontend JavaScript
 */

const API_URL = 'http://localhost:8000/api';
let token = localStorage.getItem('token');
let currentUser = null;

// ============ UTILIDADES ============
async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method,
        headers
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        if (response.status === 401) {
            logout();
            return null;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error en la solicitud');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert(error.message, 'danger');
        return null;
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-PE');
}

function getEstadoBadge(estado) {
    const badges = {
        'borrador': 'bg-secondary',
        'confirmado': 'bg-primary',
        'en_preparacion': 'bg-info',
        'listo_envio': 'bg-warning',
        'en_ruta': 'bg-purple',
        'entregado': 'bg-success',
        'cancelado': 'bg-danger',
        'pendiente': 'bg-warning',
        'asignado': 'bg-info'
    };
    return `<span class="badge ${badges[estado] || 'bg-secondary'}">${estado.replace('_', ' ')}</span>`;
}

// ============ AUTENTICACIÓN ============
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Credenciales incorrectas');
        }
        
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        
        await loadUserInfo();
        showDashboard();
        
    } catch (error) {
        showAlert(error.message, 'danger');
    }
});

async function loadUserInfo() {
    currentUser = await apiRequest('/auth/me');
    if (currentUser) {
        document.getElementById('userName').textContent = `${currentUser.nombres} ${currentUser.apellidos}`;
        document.getElementById('userRole').textContent = currentUser.rol;
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('dashboardPage').style.display = 'none';
}

document.getElementById('btnLogout').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

// ============ NAVEGACIÓN ============
function showDashboard() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'block';
    loadDashboardData();
}

function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    // Mostrar sección seleccionada
    document.getElementById(`section-${sectionName}`).classList.add('active');
    
    // Actualizar navegación
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.section === sectionName) {
            link.classList.add('active');
        }
    });
    
    // Actualizar título
    const titles = {
        'dashboard': 'Dashboard',
        'productos': 'Productos',
        'clientes': 'Clientes',
        'inventario': 'Inventario',
        'ventas': 'Ventas',
        'logistica': 'Logística'
    };
    document.getElementById('pageTitle').textContent = titles[sectionName] || sectionName;
    
    // Cargar datos de la sección
    switch (sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'productos':
            loadProductos();
            loadCategorias();
            break;
        case 'clientes':
            loadClientes();
            break;
        case 'inventario':
            loadInventario();
            loadAlmacenes();
            break;
        case 'ventas':
            loadVentas();
            break;
        case 'logistica':
            loadLogisticaDashboard();
            loadEnvios();
            loadVehiculos();
            loadConductores();
            break;
    }
}

// Event listeners para navegación
document.querySelectorAll('.sidebar .nav-link[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(link.dataset.section);
    });
});

// ============ DASHBOARD ============
async function loadDashboardData() {
    // Cargar productos
    const productos = await apiRequest('/productos?limit=1000');
    if (productos) {
        document.getElementById('totalProductos').textContent = productos.total;
    }
    
    // Cargar clientes
    const clientes = await apiRequest('/clientes?limit=1000');
    if (clientes) {
        document.getElementById('totalClientes').textContent = clientes.total;
    }
    
    // Cargar ventas
    const ventas = await apiRequest('/ventas?limit=100');
    if (ventas) {
        document.getElementById('ventasHoy').textContent = ventas.total;
        
        // Últimas ventas
        const tbody = document.getElementById('ultimasVentas');
        tbody.innerHTML = ventas.items.slice(0, 5).map(v => `
            <tr>
                <td>${v.numero}</td>
                <td>${v.cliente_id}</td>
                <td>${formatCurrency(v.total)}</td>
                <td>${getEstadoBadge(v.estado)}</td>
            </tr>
        `).join('') || '<tr><td colspan="4" class="text-center">No hay ventas</td></tr>';
    }
    
    // Productos bajo stock
    const bajoStock = await apiRequest('/productos/bajo-stock');
    const stockList = document.getElementById('stockBajo');
    if (bajoStock && bajoStock.length > 0) {
        stockList.innerHTML = bajoStock.slice(0, 5).map(p => `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${p.nombre}
                <span class="badge bg-danger rounded-pill">Bajo</span>
            </li>
        `).join('');
    } else {
        stockList.innerHTML = '<li class="list-group-item text-success">Todo el stock está bien</li>';
    }
    
    // Dashboard logística
    const logistica = await apiRequest('/logistica/dashboard');
    if (logistica) {
        document.getElementById('enviosPendientes').textContent = logistica.envios.pendientes;
    }
}

// ============ PRODUCTOS ============
async function loadProductos() {
    const busqueda = document.getElementById('buscarProducto').value;
    const categoria = document.getElementById('filtroCategoria').value;
    
    let url = '/productos?limit=100';
    if (busqueda) url += `&busqueda=${encodeURIComponent(busqueda)}`;
    if (categoria) url += `&categoria_id=${categoria}`;
    
    const data = await apiRequest(url);
    const tbody = document.getElementById('tablaProductos');
    
    if (data && data.items) {
        tbody.innerHTML = data.items.map(p => `
            <tr>
                <td>${p.codigo}</td>
                <td>${p.nombre}</td>
                <td>${p.categoria?.nombre || '-'}</td>
                <td>${formatCurrency(p.precio_venta)}</td>
                <td><span class="badge bg-${p.stock_minimo > 0 ? 'success' : 'warning'}">${p.stock_minimo}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editProducto(${p.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay productos</td></tr>';
    }
}

async function loadCategorias() {
    const data = await apiRequest('/productos/categorias');
    if (data) {
        const options = data.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');
        document.getElementById('filtroCategoria').innerHTML = '<option value="">Todas las categorías</option>' + options;
        document.getElementById('selectCategoriaProducto').innerHTML = '<option value="">Sin categoría</option>' + options;
    }
}

// Búsqueda de productos
document.getElementById('buscarProducto')?.addEventListener('input', debounce(loadProductos, 300));
document.getElementById('filtroCategoria')?.addEventListener('change', loadProductos);

// Formulario de producto
document.getElementById('formProducto').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    data.precio_compra = parseFloat(data.precio_compra) || 0;
    data.precio_venta = parseFloat(data.precio_venta) || 0;
    if (data.categoria_id) data.categoria_id = parseInt(data.categoria_id);
    else delete data.categoria_id;
    
    const result = await apiRequest('/productos', 'POST', data);
    if (result) {
        showAlert('Producto creado exitosamente', 'success');
        bootstrap.Modal.getInstance(document.getElementById('modalProducto')).hide();
        e.target.reset();
        loadProductos();
    }
});

// ============ CLIENTES ============
async function loadClientes() {
    const busqueda = document.getElementById('buscarCliente')?.value || '';
    const tipo = document.getElementById('filtroTipoCliente')?.value || '';
    
    let url = '/clientes?limit=100';
    if (busqueda) url += `&busqueda=${encodeURIComponent(busqueda)}`;
    if (tipo) url += `&tipo=${tipo}`;
    
    const data = await apiRequest(url);
    const tbody = document.getElementById('tablaClientes');
    
    if (data && data.items) {
        tbody.innerHTML = data.items.map(c => `
            <tr>
                <td>${c.codigo}</td>
                <td>${c.razon_social}</td>
                <td>${c.ruc || '-'}</td>
                <td><span class="badge bg-info">${c.tipo}</span></td>
                <td>${c.distrito || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editCliente(${c.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay clientes</td></tr>';
    }
}

document.getElementById('buscarCliente')?.addEventListener('input', debounce(loadClientes, 300));
document.getElementById('filtroTipoCliente')?.addEventListener('change', loadClientes);

document.getElementById('formCliente').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    const result = await apiRequest('/clientes', 'POST', data);
    if (result) {
        showAlert('Cliente creado exitosamente', 'success');
        bootstrap.Modal.getInstance(document.getElementById('modalCliente')).hide();
        e.target.reset();
        loadClientes();
    }
});

// ============ INVENTARIO ============
async function loadInventario() {
    const almacenId = document.getElementById('filtroAlmacen')?.value;
    
    let url = almacenId ? `/inventario/almacen/${almacenId}` : '/inventario/almacen/1';
    
    const data = await apiRequest(url);
    const tbody = document.getElementById('tablaInventario');
    
    if (data && data.length > 0) {
        tbody.innerHTML = data.map(i => `
            <tr>
                <td>${i.producto_id}</td>
                <td>${i.almacen_id}</td>
                <td><strong>${i.stock_actual}</strong></td>
                <td>${i.stock_reservado}</td>
                <td class="${i.stock_disponible < 10 ? 'text-danger' : ''}">${i.stock_disponible}</td>
                <td>${i.ubicacion || '-'}</td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay inventario</td></tr>';
    }
}

async function loadAlmacenes() {
    const data = await apiRequest('/inventario/almacenes');
    if (data) {
        const options = data.map(a => `<option value="${a.id}">${a.nombre}</option>`).join('');
        document.getElementById('filtroAlmacen').innerHTML = '<option value="">Todos los almacenes</option>' + options;
    }
}

document.getElementById('filtroAlmacen')?.addEventListener('change', loadInventario);

// ============ VENTAS ============
async function loadVentas() {
    const estado = document.getElementById('filtroEstadoVenta')?.value || '';
    
    let url = '/ventas?limit=100';
    if (estado) url += `&estado=${estado}`;
    
    const data = await apiRequest(url);
    const tbody = document.getElementById('tablaVentas');
    
    if (data && data.items) {
        tbody.innerHTML = data.items.map(v => `
            <tr>
                <td><strong>${v.numero}</strong></td>
                <td>${formatDate(v.fecha_pedido)}</td>
                <td>${v.cliente_id}</td>
                <td>${formatCurrency(v.total)}</td>
                <td>${getEstadoBadge(v.estado)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="verVenta(${v.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${v.estado === 'borrador' ? `
                        <button class="btn btn-sm btn-success" onclick="confirmarVenta(${v.id})">
                            <i class="bi bi-check"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay ventas</td></tr>';
    }
}

document.getElementById('filtroEstadoVenta')?.addEventListener('change', loadVentas);

async function confirmarVenta(id) {
    if (confirm('¿Confirmar esta venta?')) {
        const result = await apiRequest(`/ventas/${id}/confirmar`, 'POST');
        if (result) {
            showAlert('Venta confirmada', 'success');
            loadVentas();
        }
    }
}

// ============ LOGÍSTICA ============
async function loadLogisticaDashboard() {
    const data = await apiRequest('/logistica/dashboard');
    const container = document.getElementById('dashboardLogistica');
    
    if (data) {
        container.innerHTML = `
            <div class="mb-3">
                <small class="text-muted">Fecha: ${data.fecha}</small>
            </div>
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <h4 class="text-warning">${data.envios.pendientes}</h4>
                    <small>Pendientes</small>
                </div>
                <div class="col-6 mb-3">
                    <h4 class="text-info">${data.envios.en_ruta}</h4>
                    <small>En Ruta</small>
                </div>
                <div class="col-6">
                    <h4 class="text-success">${data.envios.entregados}</h4>
                    <small>Entregados</small>
                </div>
                <div class="col-6">
                    <h4 class="text-primary">${data.recursos.vehiculos_disponibles}</h4>
                    <small>Vehículos disp.</small>
                </div>
            </div>
        `;
    }
}

async function loadEnvios() {
    const data = await apiRequest('/logistica/envios/pendientes-hoy');
    const tbody = document.getElementById('tablaEnvios');
    
    if (data && data.length > 0) {
        tbody.innerHTML = data.map(e => `
            <tr>
                <td>${e.codigo}</td>
                <td>${e.venta_id}</td>
                <td>${formatDate(e.fecha_programada)}</td>
                <td>${getEstadoBadge(e.estado)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-success" onclick="completarEnvio(${e.id})">
                        <i class="bi bi-check-circle"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No hay envíos pendientes</td></tr>';
    }
}

async function loadVehiculos() {
    const data = await apiRequest('/logistica/vehiculos');
    const tbody = document.getElementById('tablaVehiculos');
    
    if (data) {
        tbody.innerHTML = data.map(v => `
            <tr>
                <td>${v.placa}</td>
                <td>${v.tipo}</td>
                <td>
                    <span class="badge ${v.disponible ? 'bg-success' : 'bg-warning'}">
                        ${v.disponible ? 'Disponible' : 'En uso'}
                    </span>
                </td>
            </tr>
        `).join('');
    }
}

async function loadConductores() {
    const data = await apiRequest('/logistica/conductores');
    const tbody = document.getElementById('tablaConductores');
    
    if (data) {
        tbody.innerHTML = data.map(c => `
            <tr>
                <td>${c.nombres} ${c.apellidos}</td>
                <td>${c.dni}</td>
                <td>
                    <span class="badge ${c.disponible ? 'bg-success' : 'bg-warning'}">
                        ${c.disponible ? 'Disponible' : 'En ruta'}
                    </span>
                </td>
            </tr>
        `).join('');
    }
}

// ============ UTILIDADES ============
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============ INICIALIZACIÓN ============
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        loadUserInfo().then(() => {
            showDashboard();
        }).catch(() => {
            logout();
        });
    }
});
