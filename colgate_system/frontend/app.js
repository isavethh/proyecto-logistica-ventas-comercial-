/**
 * Sistema de Gestión Colgate - Frontend JavaScript Mejorado
 */

const API_URL = 'http://localhost:8000/api';
let token = localStorage.getItem('token');
let currentUser = null;
let chartVentas = null;
let chartEstados = null;
let chartMensual = null;
let detalleVenta = [];

// ============ UTILIDADES ============
async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const options = { method, headers };
    if (data && method !== 'GET') options.body = JSON.stringify(data);
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        if (response.status === 401) { logout(); return null; }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error en la solicitud');
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        return null;
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast-custom ${type}`;
    const icons = { success: 'check-circle-fill', error: 'x-circle-fill', warning: 'exclamation-triangle-fill', info: 'info-circle-fill' };
    const colors = { success: '#11998e', error: '#ff416c', warning: '#f5576c', info: '#4facfe' };
    toast.innerHTML = `<i class="bi bi-${icons[type]}" style="color: ${colors[type]}; font-size: 1.2rem;"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value || 0);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-PE');
}

function getEstadoBadge(estado) {
    const badges = {
        'borrador': 'bg-secondary', 'confirmado': 'bg-primary', 'en_preparacion': 'bg-info',
        'listo_envio': 'bg-warning', 'en_ruta': 'bg-purple', 'entregado': 'bg-success',
        'cancelado': 'bg-danger', 'pendiente': 'bg-warning', 'asignado': 'bg-info'
    };
    return `<span class="badge ${badges[estado] || 'bg-secondary'}">${(estado || '').replace('_', ' ')}</span>`;
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
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        if (!response.ok) throw new Error('Credenciales incorrectas');
        
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        
        await loadUserInfo();
        showDashboard();
        showToast('Bienvenido al sistema', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
});

async function loadUserInfo() {
    currentUser = await apiRequest('/auth/me');
    if (currentUser) {
        document.getElementById('userName').textContent = `${currentUser.nombres} ${currentUser.apellidos}`;
        document.getElementById('userRole').textContent = currentUser.rol;
        document.getElementById('userAvatar').textContent = currentUser.nombres.charAt(0).toUpperCase();
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('dashboardPage').style.display = 'none';
    showToast('Sesión cerrada', 'info');
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
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(`section${sectionName.charAt(0).toUpperCase() + sectionName.slice(1)}`).classList.add('active');
    
    document.querySelectorAll('.sidebar .nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`.sidebar .nav-link[data-section="${sectionName}"]`)?.classList.add('active');
    
    const titles = {
        dashboard: 'Dashboard', productos: 'Productos', clientes: 'Clientes',
        ventas: 'Ventas', inventario: 'Inventario', logistica: 'Logística', reportes: 'Reportes'
    };
    document.getElementById('pageTitle').textContent = titles[sectionName] || 'Dashboard';
    document.getElementById('breadcrumbCurrent').textContent = titles[sectionName] || 'Dashboard';
    
    // Cargar datos de la sección
    if (sectionName === 'dashboard') loadDashboardData();
    else if (sectionName === 'productos') loadProductos();
    else if (sectionName === 'clientes') loadClientes();
    else if (sectionName === 'ventas') loadVentas();
    else if (sectionName === 'inventario') loadInventario();
    else if (sectionName === 'logistica') loadLogistica();
    else if (sectionName === 'reportes') loadReportes();
}

document.querySelectorAll('.sidebar .nav-link[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(link.dataset.section);
    });
});

// ============ DASHBOARD ============
async function loadDashboardData() {
    const stats = await apiRequest('/reportes/dashboard');
    if (!stats) return;
    
    // KPIs
    document.getElementById('kpiIngresos').textContent = formatCurrency(stats.resumen.ingresos_mes);
    document.getElementById('kpiVentas').textContent = stats.resumen.ventas_mes;
    document.getElementById('kpiClientes').textContent = stats.resumen.total_clientes;
    document.getElementById('kpiProductos').textContent = stats.resumen.total_productos;
    document.getElementById('kpiBajoStock').textContent = `${stats.resumen.productos_bajo_stock} bajo stock`;
    
    // Gráfico de ventas por día
    const ctxVentas = document.getElementById('chartVentas').getContext('2d');
    if (chartVentas) chartVentas.destroy();
    chartVentas = new Chart(ctxVentas, {
        type: 'line',
        data: {
            labels: stats.ventas_por_dia.map(v => v.fecha),
            datasets: [{
                label: 'Ventas (S/.)',
                data: stats.ventas_por_dia.map(v => v.total),
                borderColor: '#e21937',
                backgroundColor: 'rgba(226, 25, 55, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
    
    // Gráfico de estados
    const ctxEstados = document.getElementById('chartEstados').getContext('2d');
    if (chartEstados) chartEstados.destroy();
    const colores = ['#667eea', '#11998e', '#f5576c', '#4facfe', '#ff416c'];
    chartEstados = new Chart(ctxEstados, {
        type: 'doughnut',
        data: {
            labels: stats.ventas_por_estado.map(v => v.estado),
            datasets: [{
                data: stats.ventas_por_estado.map(v => v.cantidad),
                backgroundColor: colores
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
    
    // Top productos
    const topProd = document.getElementById('topProductosTable');
    topProd.innerHTML = stats.top_productos.length ? stats.top_productos.map((p, i) => `
        <tr>
            <td><span class="badge bg-secondary">${i + 1}</span></td>
            <td>${p.nombre}</td>
            <td class="text-end fw-semibold">${p.cantidad}</td>
        </tr>
    `).join('') : '<tr><td colspan="3" class="text-center text-muted">Sin datos</td></tr>';
    
    // Top clientes
    const topCli = document.getElementById('topClientesTable');
    topCli.innerHTML = stats.top_clientes.length ? stats.top_clientes.map((c, i) => `
        <tr>
            <td><span class="badge bg-secondary">${i + 1}</span></td>
            <td>${c.nombre}</td>
            <td class="text-end fw-semibold">${formatCurrency(c.total)}</td>
        </tr>
    `).join('') : '<tr><td colspan="3" class="text-center text-muted">Sin datos</td></tr>';
}

// ============ PRODUCTOS ============
async function loadProductos() {
    const productos = await apiRequest('/productos/');
    if (!productos) return;
    
    const tabla = document.getElementById('productosTable');
    tabla.innerHTML = productos.length ? productos.map(p => `
        <tr>
            <td><code>${p.codigo}</code></td>
            <td><strong>${p.nombre}</strong></td>
            <td>${p.categoria?.nombre || '-'}</td>
            <td class="fw-semibold text-success">${formatCurrency(p.precio_venta)}</td>
            <td>${p.stock_actual || 0}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarProducto(${p.id})"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarProducto(${p.id})"><i class="bi bi-trash"></i></button>
            </td>
        </tr>
    `).join('') : '<tr><td colspan="6" class="text-center text-muted">No hay productos</td></tr>';
    
    // Cargar categorías y marcas para el modal
    loadCategoriasYMarcas();
}

async function loadCategoriasYMarcas() {
    const categorias = await apiRequest('/productos/categorias/');
    const marcas = await apiRequest('/productos/marcas/');
    
    const selCat = document.getElementById('selectCategoriaProducto');
    const selMarca = document.getElementById('selectMarcaProducto');
    
    if (selCat && categorias) {
        selCat.innerHTML = '<option value="">Seleccionar...</option>' + 
            categorias.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');
    }
    if (selMarca && marcas) {
        selMarca.innerHTML = '<option value="">Seleccionar...</option>' + 
            marcas.map(m => `<option value="${m.id}">${m.nombre}</option>`).join('');
    }
}

document.getElementById('formProducto')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
        codigo: form.codigo.value,
        nombre: form.nombre.value,
        descripcion: form.descripcion?.value || '',
        categoria_id: parseInt(form.categoria_id.value),
        marca_id: form.marca_id?.value ? parseInt(form.marca_id.value) : null,
        precio_compra: parseFloat(form.precio_compra.value),
        precio_venta: parseFloat(form.precio_venta.value),
        stock_minimo: parseInt(form.stock_minimo?.value) || 10
    };
    
    const result = await apiRequest('/productos/', 'POST', data);
    if (result) {
        showToast('Producto creado exitosamente', 'success');
        bootstrap.Modal.getInstance(document.getElementById('modalProducto')).hide();
        form.reset();
        loadProductos();
    }
});

// ============ CLIENTES ============
async function loadClientes() {
    const clientes = await apiRequest('/clientes/');
    if (!clientes) return;
    
    const tabla = document.getElementById('clientesTable');
    tabla.innerHTML = clientes.length ? clientes.map(c => `
        <tr>
            <td><code>${c.ruc_dni}</code></td>
            <td><strong>${c.razon_social}</strong></td>
            <td><span class="badge bg-info">${c.tipo_cliente}</span></td>
            <td>${c.contacto_nombre || '-'}</td>
            <td>${c.email || '-'}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarCliente(${c.id})"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarCliente(${c.id})"><i class="bi bi-trash"></i></button>
            </td>
        </tr>
    `).join('') : '<tr><td colspan="6" class="text-center text-muted">No hay clientes</td></tr>';
    
    // Cargar select de clientes para ventas
    loadClientesSelect();
}

async function loadClientesSelect() {
    const clientes = await apiRequest('/clientes/');
    const select = document.getElementById('selectClienteVenta');
    if (select && clientes) {
        select.innerHTML = '<option value="">Seleccionar cliente...</option>' +
            clientes.map(c => `<option value="${c.id}">${c.razon_social}</option>`).join('');
    }
}

document.getElementById('formCliente')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
        ruc_dni: form.ruc_dni.value,
        razon_social: form.razon_social.value,
        tipo_cliente: form.tipo_cliente.value,
        email: form.email?.value || null,
        telefono: form.telefono?.value || null,
        direccion: form.direccion?.value || null
    };
    
    const result = await apiRequest('/clientes/', 'POST', data);
    if (result) {
        showToast('Cliente creado exitosamente', 'success');
        bootstrap.Modal.getInstance(document.getElementById('modalCliente')).hide();
        form.reset();
        loadClientes();
    }
});

// ============ VENTAS ============
async function loadVentas() {
    const ventas = await apiRequest('/ventas/');
    if (!ventas) return;
    
    const tabla = document.getElementById('ventasTable');
    tabla.innerHTML = ventas.length ? ventas.map(v => `
        <tr>
            <td><strong>#${v.numero_venta}</strong></td>
            <td>${formatDate(v.fecha_creacion)}</td>
            <td>${v.cliente?.razon_social || '-'}</td>
            <td class="fw-semibold text-success">${formatCurrency(v.total)}</td>
            <td>${getEstadoBadge(v.estado)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="verVenta(${v.id})"><i class="bi bi-eye"></i></button>
            </td>
        </tr>
    `).join('') : '<tr><td colspan="6" class="text-center text-muted">No hay ventas</td></tr>';
    
    // Cargar productos para el modal de venta
    loadProductosSelect();
    loadClientesSelect();
    
    // Setear fecha actual
    document.getElementById('fechaVenta').value = new Date().toISOString().split('T')[0];
}

async function loadProductosSelect() {
    const productos = await apiRequest('/productos/');
    const select = document.getElementById('selectProductoVenta');
    if (select && productos) {
        select.innerHTML = '<option value="">Seleccionar producto...</option>' +
            productos.map(p => `<option value="${p.id}" data-precio="${p.precio_venta}" data-nombre="${p.nombre}">${p.nombre} - ${formatCurrency(p.precio_venta)}</option>`).join('');
    }
}

function agregarProductoVenta() {
    const select = document.getElementById('selectProductoVenta');
    const cantidad = parseInt(document.getElementById('cantidadProducto').value) || 1;
    const precioInput = document.getElementById('precioProducto');
    
    if (!select.value) {
        showToast('Seleccione un producto', 'warning');
        return;
    }
    
    const option = select.selectedOptions[0];
    const precio = parseFloat(precioInput.value) || parseFloat(option.dataset.precio);
    
    detalleVenta.push({
        producto_id: parseInt(select.value),
        nombre: option.dataset.nombre,
        cantidad: cantidad,
        precio_unitario: precio,
        subtotal: cantidad * precio
    });
    
    renderDetalleVenta();
    select.value = '';
    precioInput.value = '';
    document.getElementById('cantidadProducto').value = 1;
}

function renderDetalleVenta() {
    const tabla = document.getElementById('detalleVentaTable');
    if (!detalleVenta.length) {
        tabla.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sin productos</td></tr>';
        document.getElementById('subtotalVenta').textContent = formatCurrency(0);
        document.getElementById('igvVenta').textContent = formatCurrency(0);
        document.getElementById('totalVenta').textContent = formatCurrency(0);
        return;
    }
    
    tabla.innerHTML = detalleVenta.map((d, i) => `
        <tr>
            <td>${d.nombre}</td>
            <td>${d.cantidad}</td>
            <td>${formatCurrency(d.precio_unitario)}</td>
            <td>${formatCurrency(d.subtotal)}</td>
            <td><button class="btn btn-sm btn-outline-danger" onclick="quitarProductoVenta(${i})"><i class="bi bi-x"></i></button></td>
        </tr>
    `).join('');
    
    const subtotal = detalleVenta.reduce((sum, d) => sum + d.subtotal, 0);
    const igv = subtotal * 0.18;
    const total = subtotal + igv;
    
    document.getElementById('subtotalVenta').textContent = formatCurrency(subtotal);
    document.getElementById('igvVenta').textContent = formatCurrency(igv);
    document.getElementById('totalVenta').textContent = formatCurrency(total);
}

function quitarProductoVenta(index) {
    detalleVenta.splice(index, 1);
    renderDetalleVenta();
}

document.getElementById('formVenta')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!detalleVenta.length) {
        showToast('Agregue al menos un producto', 'warning');
        return;
    }
    
    const form = e.target;
    const data = {
        cliente_id: parseInt(form.cliente_id.value),
        tipo_pago: form.tipo_pago.value,
        detalles: detalleVenta.map(d => ({
            producto_id: d.producto_id,
            cantidad: d.cantidad,
            precio_unitario: d.precio_unitario
        }))
    };
    
    const result = await apiRequest('/ventas/', 'POST', data);
    if (result) {
        showToast('Venta creada exitosamente', 'success');
        bootstrap.Modal.getInstance(document.getElementById('modalVenta')).hide();
        detalleVenta = [];
        renderDetalleVenta();
        form.reset();
        loadVentas();
    }
});

// ============ INVENTARIO ============
async function loadInventario() {
    const inventario = await apiRequest('/inventario/');
    const alertas = await apiRequest('/reportes/inventario/alertas');
    
    if (alertas) {
        document.getElementById('invBajoStock').textContent = alertas.stock_bajo?.length || 0;
        document.getElementById('invSinStock').textContent = alertas.sin_stock?.length || 0;
        document.getElementById('invStockNormal').textContent = alertas.stock_alto?.length || 0;
    }
    
    if (!inventario) return;
    
    const tabla = document.getElementById('inventarioTable');
    tabla.innerHTML = inventario.length ? inventario.map(i => {
        let estado = 'bg-success';
        let estadoText = 'Normal';
        if (i.cantidad === 0) { estado = 'bg-danger'; estadoText = 'Sin Stock'; }
        else if (i.cantidad <= i.producto?.stock_minimo) { estado = 'bg-warning'; estadoText = 'Bajo'; }
        
        return `
            <tr>
                <td><strong>${i.producto?.nombre || '-'}</strong></td>
                <td>${i.almacen?.nombre || '-'}</td>
                <td class="fw-semibold">${i.cantidad}</td>
                <td>${i.producto?.stock_minimo || 0}</td>
                <td><span class="badge ${estado}">${estadoText}</span></td>
            </tr>
        `;
    }).join('') : '<tr><td colspan="5" class="text-center text-muted">No hay inventario</td></tr>';
}

// ============ LOGÍSTICA ============
async function loadLogistica() {
    const envios = await apiRequest('/logistica/envios/');
    
    let pendientes = 0, enRuta = 0, entregados = 0;
    if (envios) {
        envios.forEach(e => {
            if (e.estado === 'pendiente') pendientes++;
            else if (e.estado === 'en_ruta') enRuta++;
            else if (e.estado === 'entregado') entregados++;
        });
    }
    
    document.getElementById('logPendientes').textContent = pendientes;
    document.getElementById('logEnRuta').textContent = enRuta;
    document.getElementById('logEntregados').textContent = entregados;
    
    const zonas = await apiRequest('/logistica/zonas/');
    document.getElementById('logZonas').textContent = zonas?.length || 0;
    
    const tabla = document.getElementById('enviosTable');
    tabla.innerHTML = envios?.length ? envios.map(e => `
        <tr>
            <td><strong>#${e.id}</strong></td>
            <td>${e.venta?.numero_venta || '-'}</td>
            <td>${e.direccion_destino || '-'}</td>
            <td>${formatDate(e.fecha_programada)}</td>
            <td>${getEstadoBadge(e.estado)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></button>
            </td>
        </tr>
    `).join('') : '<tr><td colspan="6" class="text-center text-muted">No hay envíos</td></tr>';
}

// ============ REPORTES ============
async function loadReportes() {
    const kpis = await apiRequest('/reportes/kpis');
    const mensual = await apiRequest('/reportes/ventas/mensual');
    
    if (kpis) {
        document.getElementById('kpiConversion').textContent = `${kpis.tasa_conversion}%`;
        document.getElementById('progressConversion').style.width = `${kpis.tasa_conversion}%`;
        document.getElementById('kpiTicket').textContent = formatCurrency(kpis.ticket_promedio);
        document.getElementById('kpiNuevosClientes').textContent = kpis.clientes_nuevos;
        document.getElementById('kpiTotalOrdenes').textContent = kpis.total_ordenes;
    }
    
    if (mensual) {
        const ctx = document.getElementById('chartMensual').getContext('2d');
        if (chartMensual) chartMensual.destroy();
        chartMensual = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: mensual.datos.map(d => d.nombre_mes),
                datasets: [{
                    label: 'Ventas (S/.)',
                    data: mensual.datos.map(d => d.total),
                    backgroundColor: 'rgba(226, 25, 55, 0.8)',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

// ============ INICIALIZACIÓN ============
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        loadUserInfo().then(() => showDashboard());
    }
    
    // Event listener para buscar productos
    document.getElementById('searchProducto')?.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        document.querySelectorAll('#productosTable tr').forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
    
    // Event listener para buscar clientes
    document.getElementById('searchCliente')?.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        document.querySelectorAll('#clientesTable tr').forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
    
    // Cambiar precio al seleccionar producto en venta
    document.getElementById('selectProductoVenta')?.addEventListener('change', function() {
        const option = this.selectedOptions[0];
        if (option && option.dataset.precio) {
            document.getElementById('precioProducto').value = option.dataset.precio;
        }
    });
});
