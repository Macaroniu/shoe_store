const API_BASE_URL = 'http://localhost:8000';

let currentUser = null;
let authToken = null;
let allProducts = [];
let allOrders = [];
let suppliers = [];
let pickupPoints = [];
let editingProduct = null;
let editingOrder = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
});

function checkAuth() {
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');

    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showProductsScreen();
    } else {
        showScreen('loginScreen');
    }
}

function setupEventListeners() {
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('productForm').addEventListener('submit', handleProductSubmit);
    document.getElementById('orderForm').addEventListener('submit', handleOrderSubmit);
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('loginError');

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Неверный логин или пароль');
        }

        const data = await response.json();

        authToken = data.access_token;
        currentUser = data.user;

        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showProductsScreen();

    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.classList.add('active');
    }
}

function enterAsGuest() {
    currentUser = { role: 'Гость', full_name: 'Гость' };
    authToken = null;
    showProductsScreen();
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    authToken = null;
    currentUser = null;
    showScreen('loginScreen');
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

async function showProductsScreen() {
    showScreen('productsScreen');
    updateSidebarUserInfo();
    setupControlPanel();
    updateNavigation();
    await loadProducts();
}

async function showOrdersScreen() {
    if (!canViewOrders()) {
        alert('У вас нет прав для просмотра заказов');
        return;
    }

    showScreen('ordersScreen');
    updateSidebarUserInfoOrders();
    updateNavigationOrders();

    if (isAdmin()) {
        document.getElementById('ordersAdminActions').style.display = 'flex';
    }

    await loadOrders();
}

function updateSidebarUserInfo() {
    if (currentUser) {
        document.getElementById('sidebarUserName').textContent = currentUser.full_name;
        document.getElementById('sidebarUserRole').textContent = currentUser.role;
    }
}

function updateSidebarUserInfoOrders() {
    if (currentUser) {
        document.getElementById('sidebarUserNameOrders').textContent = currentUser.full_name;
        document.getElementById('sidebarUserRoleOrders').textContent = currentUser.role;
    }
}

function updateNavigation() {
    const ordersNavItem = document.getElementById('ordersNavItem');
    if (canViewOrders()) {
        ordersNavItem.style.display = 'flex';
    } else {
        ordersNavItem.style.display = 'none';
    }
}

function updateNavigationOrders() {
}

function setupControlPanel() {
    const controlPanel = document.getElementById('controlPanel');
    const adminHeaderActions = document.getElementById('adminHeaderActions');

    if (canFilterProducts()) {
        controlPanel.style.display = 'block';
        loadSuppliers();
    } else {
        controlPanel.style.display = 'none';
    }

    if (isAdmin()) {
        adminHeaderActions.style.display = 'flex';
    } else {
        adminHeaderActions.style.display = 'none';
    }
}

function isAdmin() {
    return currentUser && currentUser.role === 'Администратор';
}

function isManagerOrAdmin() {
    return currentUser && (currentUser.role === 'Менеджер' || currentUser.role === 'Администратор');
}

function canFilterProducts() {
    return isManagerOrAdmin();
}

function canViewOrders() {
    return isManagerOrAdmin();
}

async function loadProducts() {
    const gridEl = document.getElementById('productsGrid');
    gridEl.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Загрузка товаров...</p></div>';

    try {
        let url = `${API_BASE_URL}/api/products`;
        const params = new URLSearchParams();

        if (canFilterProducts()) {
            const search = document.getElementById('searchInput').value;
            const supplier = document.getElementById('supplierFilter').value;
            const sort = document.getElementById('sortQuantity').value;

            if (search) params.append('search', search);
            if (supplier) params.append('supplier', supplier);
            if (sort) params.append('sort_by_quantity', sort);
        }

        if (params.toString()) {
            url += '?' + params.toString();
        }

        const headers = {};
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch(url, { headers });

        if (!response.ok) {
            throw new Error('Ошибка загрузки товаров');
        }

        allProducts = await response.json();
        renderProducts();

    } catch (error) {
        gridEl.innerHTML = `<div class="loading-state"><p>Ошибка: ${error.message}</p></div>`;
    }
}

function renderProducts() {
    const gridEl = document.getElementById('productsGrid');

    if (allProducts.length === 0) {
        gridEl.innerHTML = '<div class="loading-state"><p>Товары не найдены</p></div>';
        return;
    }

    gridEl.innerHTML = '';

    allProducts.forEach(product => {
        const card = createProductCard(product);
        gridEl.appendChild(card);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    if (product.discount > 15) {
        card.classList.add('high-discount');
    }
    if (product.out_of_stock) {
        card.classList.add('out-of-stock');
    }

    const hasDiscount = product.discount > 0;
    const imageUrl = product.photo.startsWith('http') ? product.photo : `${API_BASE_URL}${product.photo}`;

    card.innerHTML = `
        <div class="product-image-container">
            <img src="${imageUrl}" alt="${product.name}" class="product-image" onerror="this.src='${API_BASE_URL}/static/images/picture.png'">
            ${hasDiscount ? `<div class="discount-badge">-${product.discount}%</div>` : ''}
        </div>
        <div class="product-info">
            <h3>${product.name}</h3>
            <p><strong>📦</strong> ${product.article}</p>
            <p><strong>🏷️</strong> ${product.category}</p>
            <p><strong>🏭</strong> ${product.manufacturer}</p>
            <p><strong>🚚</strong> ${product.supplier}</p>
            <p><strong>📊</strong> ${product.quantity} ${product.unit}</p>
            ${product.description ? `<p style="margin-top: 10px; color: #666;">${product.description}</p>` : ''}

            <div class="product-price">
                ${hasDiscount ? `<span class="original-price">${product.price.toFixed(2)} ₽</span>` : ''}
                <span class="final-price">${product.final_price.toFixed(2)} ₽</span>
            </div>
        </div>
        ${isAdmin() ? `
            <div class="product-actions">
                <button class="btn btn-accent btn-sm" onclick="editProduct('${product.article}')">✏️ Редактировать</button>
                <button class="btn btn-danger btn-sm" onclick="deleteProduct('${product.article}')">🗑️ Удалить</button>
            </div>
        ` : ''}
    `;

    return card;
}

async function loadSuppliers() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/products/suppliers`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            suppliers = await response.json();
            const selectEl = document.getElementById('supplierFilter');
            selectEl.innerHTML = suppliers.map(s => `<option value="${s}">${s}</option>`).join('');
        }
    } catch (error) {
        console.error('Ошибка загрузки поставщиков:', error);
    }
}

function applyFilters() {
    loadProducts();
}

async function showAddProductModal() {
    editingProduct = null;
    document.getElementById('productModalTitle').textContent = 'Добавить товар';
    document.getElementById('productForm').reset();
    document.getElementById('article').disabled = false;
    document.getElementById('productModal').classList.add('active');
}

async function editProduct(article) {
    editingProduct = allProducts.find(p => p.article === article);
    if (!editingProduct) return;

    document.getElementById('productModalTitle').textContent = 'Редактировать товар';
    document.getElementById('productArticle').value = editingProduct.article;
    document.getElementById('article').value = editingProduct.article;
    document.getElementById('article').disabled = true;
    document.getElementById('name').value = editingProduct.name;
    document.getElementById('category').value = editingProduct.category;
    document.getElementById('manufacturer').value = editingProduct.manufacturer;
    document.getElementById('supplier').value = editingProduct.supplier;
    document.getElementById('unit').value = editingProduct.unit;
    document.getElementById('price').value = editingProduct.price;
    document.getElementById('discount').value = editingProduct.discount;
    document.getElementById('quantity').value = editingProduct.quantity;
    document.getElementById('description').value = editingProduct.description || '';

    document.getElementById('productModal').classList.add('active');
}

function closeProductModal() {
    document.getElementById('productModal').classList.remove('active');
    document.getElementById('productError').classList.remove('active');
    editingProduct = null;
}

async function handleProductSubmit(e) {
    e.preventDefault();

    const errorEl = document.getElementById('productError');
    errorEl.classList.remove('active');

    const productData = {
        article: document.getElementById('article').value,
        name: document.getElementById('name').value,
        category: document.getElementById('category').value,
        manufacturer: document.getElementById('manufacturer').value,
        supplier: document.getElementById('supplier').value,
        unit: document.getElementById('unit').value,
        price: parseFloat(document.getElementById('price').value),
        discount: parseInt(document.getElementById('discount').value) || 0,
        quantity: parseInt(document.getElementById('quantity').value),
        description: document.getElementById('description').value || null
    };

    try {
        const url = editingProduct
            ? `${API_BASE_URL}/api/products/${editingProduct.article}`
            : `${API_BASE_URL}/api/products`;

        const method = editingProduct ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения товара');
        }

        const savedProduct = await response.json();

        const photoFile = document.getElementById('photo').files[0];
        if (photoFile) {
            await uploadProductImage(savedProduct.article, photoFile);
        }

        closeProductModal();
        await loadProducts();

    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.classList.add('active');
    }
}

async function uploadProductImage(article, file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/products/${article}/upload-image`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    });

    if (!response.ok) {
        throw new Error('Ошибка загрузки изображения');
    }
}

async function deleteProduct(article) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/products/${article}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка удаления товара');
        }

        await loadProducts();

    } catch (error) {
        alert(error.message);
    }
}

async function loadOrders() {
    const listEl = document.getElementById('ordersList');
    listEl.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Загрузка заказов...</p></div>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/orders`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка загрузки заказов');
        }

        allOrders = await response.json();
        renderOrders();

    } catch (error) {
        listEl.innerHTML = `<div class="loading-state"><p>Ошибка: ${error.message}</p></div>`;
    }
}

function renderOrders() {
    const listEl = document.getElementById('ordersList');

    if (allOrders.length === 0) {
        listEl.innerHTML = '<div class="loading-state"><p>Заказы не найдены</p></div>';
        return;
    }

    listEl.innerHTML = '';

    allOrders.forEach(order => {
        const card = createOrderCard(order);
        listEl.appendChild(card);
    });
}

function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';

    const statusClass = order.status === 'Новый' ? 'new' : 'completed';

    card.innerHTML = `
        <div class="order-header">
            <span class="order-number">Заказ № ${order.order_number}</span>
            <span class="order-status ${statusClass}">${order.status}</span>
        </div>
        <div class="order-info">
            <div class="order-info-item">
                <label>Дата заказа</label>
                <span>📅 ${formatDate(order.order_date)}</span>
            </div>
            <div class="order-info-item">
                <label>Дата выдачи</label>
                <span>📅 ${formatDate(order.delivery_date)}</span>
            </div>
            <div class="order-info-item">
                <label>Клиент</label>
                <span>👤 ${order.client_full_name}</span>
            </div>
            <div class="order-info-item">
                <label>Код получения</label>
                <span>🔑 ${order.code}</span>
            </div>
            <div class="order-info-item">
                <label>Пункт выдачи</label>
                <span>📍 ${order.pickup_address || 'Не указан'}</span>
            </div>
        </div>
        ${isAdmin() ? `
            <div class="order-actions">
                <button class="btn btn-accent btn-sm" onclick="editOrder(${order.id})">✏️ Редактировать</button>
                <button class="btn btn-danger btn-sm" onclick="deleteOrder(${order.id})">🗑️ Удалить</button>
            </div>
        ` : ''}
    `;

    return card;
}

async function showAddOrderModal() {
    editingOrder = null;
    document.getElementById('orderModalTitle').textContent = 'Добавить заказ';
    document.getElementById('orderForm').reset();

    const today = new Date().toISOString().split('T')[0];
    document.getElementById('orderDate').value = today;

    document.getElementById('orderProducts').innerHTML = '<button type="button" class="btn btn-ghost btn-sm" onclick="addProductToOrder()">+ Добавить товар</button>';

    await loadPickupPoints();
    document.getElementById('orderModal').classList.add('active');
}

async function editOrder(orderId) {
    editingOrder = allOrders.find(o => o.id === orderId);
    if (!editingOrder) return;

    document.getElementById('orderModalTitle').textContent = 'Редактировать заказ';
    document.getElementById('orderId').value = editingOrder.id;
    document.getElementById('orderDate').value = editingOrder.order_date;
    document.getElementById('deliveryDate').value = editingOrder.delivery_date;
    document.getElementById('clientName').value = editingOrder.client_full_name;
    document.getElementById('code').value = editingOrder.code;
    document.getElementById('status').value = editingOrder.status;

    await loadPickupPoints();
    document.getElementById('pickupPoint').value = editingOrder.pickup_point_id;

    document.getElementById('orderModal').classList.add('active');
}

function closeOrderModal() {
    document.getElementById('orderModal').classList.remove('active');
    document.getElementById('orderError').classList.remove('active');
    editingOrder = null;
}

async function loadPickupPoints() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders/pickup-points`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            pickupPoints = await response.json();
            const selectEl = document.getElementById('pickupPoint');
            selectEl.innerHTML = '<option value="">Выберите пункт выдачи</option>' +
                pickupPoints.map(p => `<option value="${p.id}">${p.address}</option>`).join('');
        }
    } catch (error) {
        console.error('Ошибка загрузки пунктов выдачи:', error);
    }
}

function addProductToOrder() {
    const container = document.getElementById('orderProducts');
    const item = document.createElement('div');
    item.className = 'order-product-item';

    const productOptions = allProducts.map(p =>
        `<option value="${p.article}">${p.name} (${p.article})</option>`
    ).join('');

    item.innerHTML = `
        <select class="order-product-select" required>
            <option value="">Выберите товар</option>
            ${productOptions}
        </select>
        <input type="number" class="order-product-quantity" min="1" value="1" placeholder="Кол-во" required>
        <button type="button" class="btn btn-danger btn-sm" onclick="this.parentElement.remove()">×</button>
    `;

    container.insertBefore(item, container.firstChild);
}

async function handleOrderSubmit(e) {
    e.preventDefault();

    const errorEl = document.getElementById('orderError');
    errorEl.classList.remove('active');

    const productItems = document.querySelectorAll('.order-product-item');
    const products = [];

    productItems.forEach(item => {
        const productId = item.querySelector('.order-product-select').value;
        const quantity = parseInt(item.querySelector('.order-product-quantity').value);

        if (productId && quantity > 0) {
            products.push({ product_id: productId, quantity });
        }
    });

    if (products.length === 0) {
        errorEl.textContent = 'Добавьте хотя бы один товар в заказ';
        errorEl.classList.add('active');
        return;
    }

    const orderData = {
        order_date: document.getElementById('orderDate').value,
        delivery_date: document.getElementById('deliveryDate').value,
        pickup_point_id: parseInt(document.getElementById('pickupPoint').value),
        client_full_name: document.getElementById('clientName').value,
        code: parseInt(document.getElementById('code').value),
        status: document.getElementById('status').value,
        products: products
    };

    try {
        const url = editingOrder
            ? `${API_BASE_URL}/api/orders/${editingOrder.id}`
            : `${API_BASE_URL}/api/orders`;

        const method = editingOrder ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения заказа');
        }

        closeOrderModal();
        await loadOrders();

    } catch (error) {
        errorEl.textContent = error.message;
        errorEl.classList.add('active');
    }
}

async function deleteOrder(orderId) {
    if (!confirm('Вы уверены, что хотите удалить этот заказ?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/orders/${orderId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка удаления заказа');
        }

        await loadOrders();

    } catch (error) {
        alert(error.message);
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}