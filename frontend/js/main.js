const API_BASE_URL = 'http://localhost:8000/api';

// Global state
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Utility functions
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-top toast-end`;
    toast.innerHTML = `
        <div class="alert alert-${type}">
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function formatPrice(price) {
    return `$${parseFloat(price).toFixed(2)}`;
}

// Cart management
function addToCart(product) {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            ...product,
            quantity: 1
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showToast('Product added to cart!', 'success');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showToast('Product removed from cart!', 'info');
}

function updateCartCount() {
    const cartCount = document.getElementById('cartCount');
    const cartItemsCount = document.getElementById('cartItemsCount');
    const cartTotal = document.getElementById('cartTotal');
    
    if (cartCount) {
        cartCount.textContent = cart.reduce((total, item) => total + item.quantity, 0);
    }
    
    if (cartItemsCount) {
        cartItemsCount.textContent = `${cart.reduce((total, item) => total + item.quantity, 0)} Items`;
    }
    
    if (cartTotal) {
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        cartTotal.textContent = `Subtotal: ${formatPrice(total)}`;
    }
}

function viewCart() {
    window.location.href = 'cart.html';
}

// Product management
async function loadFeaturedProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/medicines/featured`);
        if (!response.ok) throw new Error('Failed to fetch products');
        
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Error loading products:', error);
        // Fallback to sample products
        displaySampleProducts();
    }
}

async function loadAllProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/medicines`);
        if (!response.ok) throw new Error('Failed to fetch products');
        
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Error loading products:', error);
        displaySampleProducts();
    }
}

function displayProducts(products) {
    const productsGrid = document.getElementById('productsGrid');
    if (!productsGrid) return;

    productsGrid.innerHTML = products.map(product => `
        <div class="card bg-base-100 shadow-md service-card">
            <figure class="px-4 pt-4">
                <div class="w-full h-32 bg-gray-100 rounded-lg flex items-center justify-center">
                    <i class="fas fa-pills text-4xl text-green-600"></i>
                </div>
            </figure>
            <div class="card-body items-center text-center p-4">
                <h3 class="card-title text-sm">${product.name}</h3>
                <p class="text-green-600 font-bold">${formatPrice(product.price)}</p>
                <p class="text-xs text-gray-500">${product.manufacturer}</p>
                <div class="card-actions mt-2">
                    <button class="btn btn-primary btn-sm" onclick="addToCart(${JSON.stringify(product).replace(/"/g, '&quot;')})">
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function displaySampleProducts() {
    const sampleProducts = [
        {
            id: 1,
            name: "Napa",
            price: 200.00,
            manufacturer: "Beximco",
            description: "Pain reliever and fever reducer"
        },
        {
            id: 2,
            name: "Disprin",
            price: 250.00,
            manufacturer: "Square",
            description: "Pain reliever tablet"
        },
        {
            id: 3,
            name: "Levofox",
            price: 500.00,
            manufacturer: "Incepta",
            description: "Antibiotic medication"
        },
        {
            id: 4,
            name: "Iron Complex",
            price: 400.00,
            manufacturer: "Drug International",
            description: "Iron supplement"
        },
        {
            id: 5,
            name: "Nutraflex",
            price: 300.00,
            manufacturer: "ACI",
            description: "Joint health supplement"
        }
    ];

    displayProducts(sampleProducts);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
    updateCartCount();
    loadFeaturedProducts();
    
    // Animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.service-card, .card').forEach(el => {
        observer.observe(el);
    });
});