const API_BASE = 'http://127.0.0.1:8000/api/v1';
let token = localStorage.getItem('token');
let currentUser = null;
let cart = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        loadCurrentUser();
    } else {
        showSection('auth-section');
    }
});

// Auth Functions
function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.querySelectorAll('.auth-tab')[0].classList.add('active');
    document.querySelectorAll('.auth-tab')[1].classList.remove('active');
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    document.querySelectorAll('.auth-tab')[0].classList.remove('active');
    document.querySelectorAll('.auth-tab')[1].classList.add('active');
}

async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) throw new Error('Login failed');
        
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        
        await loadCurrentUser();
    } catch (error) {
        document.getElementById('login-error').textContent = 'Invalid credentials';
    }
}

async function register() {
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const role = document.getElementById('register-role').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role })
        });
        
        if (!response.ok) throw new Error('Registration failed');
        
        alert('Registration successful! Please login.');
        showLogin();
    } catch (error) {
        document.getElementById('register-error').textContent = 'Registration failed';
    }
}

async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Auth failed');
        
        currentUser = await response.json();
        updateNavigation();
        
        if (currentUser.role === 'admin') {
            showSection('admin-section');
            loadAdminDashboard();
        } else {
            showSection('products-section');
            loadProducts();
        }
    } catch (error) {
        logout();
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    showSection('auth-section');
    updateNavigation();
}

function updateNavigation() {
    const navLinks = document.getElementById('nav-links');
    
    if (currentUser) {
        navLinks.innerHTML = `
            <span>Welcome, ${currentUser.email}</span>
            ${currentUser.role === 'admin' ? '<button onclick="showDashboard()">Dashboard</button>' : ''}
            <button onclick="showProducts()">Products</button>
            <button onclick="showCart()">Cart (${cart.length})</button>
            <button onclick="showOrders()">My Orders</button>
            <button onclick="logout()">Logout</button>
        `;
    } else {
        navLinks.innerHTML = '';
    }
}

// Section Management
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById(sectionId).style.display = 'block';
}

function showDashboard() {
    showSection('admin-section');
    loadAdminDashboard();
}

function showProducts() {
    showSection('products-section');
    loadProducts();
}

function showCart() {
    showSection('cart-section');
    renderCart();
}

function showOrders() {
    showSection('orders-section');
    loadOrders();
}

// Products
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/?skip=0&limit=10`);
        const products = await response.json();
        
        const grid = document.getElementById('products-grid');
        grid.innerHTML = products.map(product => `
            <div class="product-card">
                <h3>${product.name}</h3>
                <p>${product.description || ''}</p>
                <p class="product-price">$${product.price.toFixed(2)}</p>
                <p>Category: ${product.category || 'N/A'}</p>
                <button onclick="addToCart(${product.id}, '${product.name}', ${product.price})">
                    Add to Cart
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

// Cart
function addToCart(productId, productName, price) {
    const existing = cart.find(item => item.product_id === productId);
    
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ product_id: productId, name: productName, price, quantity: 1 });
    }
    
    updateNavigation();
    alert(`${productName} added to cart!`);
}

function renderCart() {
    const container = document.getElementById('cart-items');
    
    if (cart.length === 0) {
        container.innerHTML = '<p>Your cart is empty</p>';
        document.getElementById('cart-total').textContent = '0.00';
        return;
    }
    
    container.innerHTML = cart.map((item, index) => `
        <div class="cart-item">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <p>$${item.price.toFixed(2)} x ${item.quantity}</p>
            </div>
            <div class="cart-item-actions">
                <button onclick="updateCartQuantity(${index}, -1)">-</button>
                <span>${item.quantity}</span>
                <button onclick="updateCartQuantity(${index}, 1)">+</button>
                <button class="btn-danger" onclick="removeFromCart(${index})">Remove</button>
            </div>
        </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('cart-total').textContent = total.toFixed(2);
}

function updateCartQuantity(index, change) {
    cart[index].quantity += change;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    renderCart();
    updateNavigation();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    renderCart();
    updateNavigation();
}

async function placeOrder() {
    if (cart.length === 0) return alert('Cart is empty!');
    
    const orderData = {
        items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        }))
    };
    
    try {
        const response = await fetch(`${API_BASE}/orders/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(orderData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        alert('Order placed successfully!');
        cart = [];
        updateNavigation();
        showOrders();
    } catch (error) {
        alert(`Order failed: ${error.message}`);
    }
}

// Orders
async function loadOrders() {
    try {
        const response = await fetch(`${API_BASE}/orders/my-orders`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const orders = await response.json();
        const container = document.getElementById('orders-list');
        
        if (orders.length === 0) {
            container.innerHTML = '<p>No orders yet</p>';
            return;
        }
        
        container.innerHTML = orders.map(order => `
            <div class="order-card">
                <div class="order-header">
                    <div>
                        <strong>Order #${order.id}</strong>
                        <p>${new Date(order.created_at).toLocaleString()}</p>
                    </div>
                    <div>
                        <span class="order-status ${order.status}">${order.status}</span>
                        <p><strong>$${order.total_amount.toFixed(2)}</strong></p>
                    </div>
                </div>
                <div class="order-items">
                    ${order.items.map(item => `
                        <p>Product #${item.product_id} - Qty: ${item.quantity} @ $${item.unit_price.toFixed(2)}</p>
                    `).join('')}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load orders:', error);
    }
}

// Admin Dashboard
async function loadAdminDashboard() {
    await loadDashboardStats();
    await loadTopSellingChart();
    await loadRevenueTimeChart();
    await loadRevenueByProduct();
}

async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/analytics/dashboard-stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const stats = await response.json();
        
        document.getElementById('stat-revenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
        document.getElementById('stat-orders').textContent = stats.total_orders;
        document.getElementById('stat-products').textContent = stats.total_products_sold;
        document.getElementById('stat-pending').textContent = stats.pending_orders;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadTopSellingChart() {
    try {
        const response = await fetch(`${API_BASE}/analytics/top-selling?limit=10`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        const ctx = document.getElementById('topSellingChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(p => p.name),
                datasets: [{
                    label: 'Units Sold',
                    data: data.map(p => p.total_sold),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load top selling:', error);
    }
}

async function loadRevenueTimeChart() {
    try {
        const response = await fetch(`${API_BASE}/analytics/revenue-over-time?days=30`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        const ctx = document.getElementById('revenueTimeChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(d => d.revenue),
                    borderColor: 'rgba(46, 204, 113, 1)',
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load revenue time:', error);
    }
}

async function loadRevenueByProduct() {
    try {
        const response = await fetch(`${API_BASE}/analytics/revenue-by-product`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        const tbody = document.getElementById('revenue-table-body');
        tbody.innerHTML = data.map(product => `
            <tr>
                <td>${product.name}</td>
                <td>${product.category || 'N/A'}</td>
                <td>${product.units_sold}</td>
                <td>$${product.revenue.toFixed(2)}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load revenue by product:', error);
    }
}
// Product Management Functions
function showCreateProduct() {
    const container = document.getElementById('all-products-list');
    
    container.innerHTML = `
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h4>Create New Product</h4>
            <input type="text" id="new-product-name" placeholder="Product Name" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
            <textarea id="new-product-description" placeholder="Description" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px; resize: vertical;"></textarea>
            <input type="number" id="new-product-price" placeholder="Price" step="0.01" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
            <input type="text" id="new-product-category" placeholder="Category" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
            <input type="number" id="new-product-quantity" placeholder="Initial Stock Quantity" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button onclick="createProduct()" class="btn-primary">Create Product</button>
                <button onclick="loadAllProducts()" class="btn-danger">Cancel</button>
            </div>
        </div>
        <div id="product-list"></div>
    `;
    
    loadAllProducts();
}

async function createProduct() {
    const name = document.getElementById('new-product-name').value;
    const description = document.getElementById('new-product-description').value;
    const price = parseFloat(document.getElementById('new-product-price').value);
    const category = document.getElementById('new-product-category').value;
    const quantity = parseInt(document.getElementById('new-product-quantity').value) || 0;
    
    if (!name || !price) {
        return alert('Name and Price are required!');
    }
    
    try {
        // Create product
        const productResponse = await fetch(`${API_BASE}/products/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, description, price, category })
        });
        
        if (!productResponse.ok) throw new Error('Failed to create product');
        
        const product = await productResponse.json();
        
        // Create inventory if quantity provided
        if (quantity > 0) {
            await fetch(`${API_BASE}/inventory/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ product_id: product.id, quantity })
            });
        }
        
        alert('Product created successfully!');
        showCreateProduct(); // Refresh the view
    } catch (error) {
        alert(`Failed to create product: ${error.message}`);
    }
}

async function loadAllProducts() {
    try {
        const response = await fetch(`${API_BASE}/products/?skip=0&limit=10`);
        const products = await response.json();
        
        const container = document.getElementById('product-list') || 
                         document.getElementById('all-products-list');
        
        if (!container) return;
        
        container.innerHTML = `
            <h4 style="margin-top: 20px;">Existing Products</h4>
            <div style="display: grid; gap: 15px; margin-top: 15px;">
                ${products.map(product => `
                    <div style="border: 2px solid #e0e0e0; border-radius: 8px; padding: 15px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4>${product.name}</h4>
                            <p style="color: #666;">${product.description || 'No description'}</p>
                            <p><strong>Price:</strong> $${product.price.toFixed(2)} | <strong>Category:</strong> ${product.category || 'N/A'}</p>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="editProduct(${product.id})" style="padding: 8px 16px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">Edit</button>
                            <button onclick="deleteProduct(${product.id})" class="btn-danger">Delete</button>
                            <button onclick="manageInventory(${product.id})" style="padding: 8px 16px; background: #2ecc71; color: white; border: none; border-radius: 5px; cursor: pointer;">Inventory</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Failed to delete');
        
        alert('Product deleted successfully!');
        showCreateProduct(); // Refresh
    } catch (error) {
        alert(`Failed to delete product: ${error.message}`);
    }
}

async function editProduct(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        const product = await response.json();
        
        const container = document.getElementById('all-products-list');
        container.innerHTML = `
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4>Edit Product</h4>
                <input type="text" id="edit-product-name" value="${product.name}" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
                <textarea id="edit-product-description" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px; resize: vertical;">${product.description || ''}</textarea>
                <input type="number" id="edit-product-price" value="${product.price}" step="0.01" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
                <input type="text" id="edit-product-category" value="${product.category || ''}" style="width: 100%; padding: 10px; margin: 5px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <button onclick="updateProduct(${productId})" class="btn-primary">Update Product</button>
                    <button onclick="showCreateProduct()" class="btn-danger">Cancel</button>
                </div>
            </div>
        `;
    } catch (error) {
        alert('Failed to load product details');
    }
}

async function updateProduct(productId) {
    const name = document.getElementById('edit-product-name').value;
    const description = document.getElementById('edit-product-description').value;
    const price = parseFloat(document.getElementById('edit-product-price').value);
    const category = document.getElementById('edit-product-category').value;
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, description, price, category })
        });
        
        if (!response.ok) throw new Error('Failed to update');
        
        alert('Product updated successfully!');
        showCreateProduct(); // Refresh
    } catch (error) {
        alert(`Failed to update product: ${error.message}`);
    }
}

async function manageInventory(productId) {
    try {
        // Try to get existing inventory
        let inventory;
        try {
            const response = await fetch(`${API_BASE}/inventory/${productId}`);
            if (response.ok) {
                inventory = await response.json();
            }
        } catch (e) {
            // Inventory doesn't exist
        }
        
        const container = document.getElementById('all-products-list');
        container.innerHTML = `
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4>Manage Inventory for Product #${productId}</h4>
                ${inventory ? `
                    <p><strong>Current Stock:</strong> ${inventory.quantity}</p>
                    <p><strong>Reserved:</strong> ${inventory.reserved_quantity}</p>
                    <p><strong>Available:</strong> ${inventory.quantity - inventory.reserved_quantity}</p>
                    <input type="number" id="inventory-quantity" value="${inventory.quantity}" style="width: 100%; padding: 10px; margin: 10px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
                    <button onclick="updateInventory(${productId})" class="btn-primary">Update Stock</button>
                ` : `
                    <p>No inventory record exists for this product.</p>
                    <input type="number" id="inventory-quantity" placeholder="Initial Quantity" style="width: 100%; padding: 10px; margin: 10px 0; border: 2px solid #e0e0e0; border-radius: 8px;">
                    <button onclick="createInventory(${productId})" class="btn-primary">Create Inventory</button>
                `}
                <button onclick="showCreateProduct()" class="btn-danger" style="margin-left: 10px;">Back</button>
            </div>
        `;
    } catch (error) {
        alert('Failed to load inventory');
    }
}

async function createInventory(productId) {
    const quantity = parseInt(document.getElementById('inventory-quantity').value);
    
    if (!quantity || quantity < 0) {
        return alert('Please enter a valid quantity');
    }
    
    try {
        const response = await fetch(`${API_BASE}/inventory/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity })
        });
        
        if (!response.ok) throw new Error('Failed to create inventory');
        
        alert('Inventory created successfully!');
        showCreateProduct();
    } catch (error) {
        alert(`Failed to create inventory: ${error.message}`);
    }
}

async function updateInventory(productId) {
    const quantity = parseInt(document.getElementById('inventory-quantity').value);
    
    if (quantity < 0) {
        return alert('Quantity cannot be negative');
    }
    
    try {
        const response = await fetch(`${API_BASE}/inventory/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ quantity })
        });
        
        if (!response.ok) throw new Error('Failed to update inventory');
        
        alert('Inventory updated successfully!');
        showCreateProduct();
    } catch (error) {
        alert(`Failed to update inventory: ${error.message}`);
    }
}