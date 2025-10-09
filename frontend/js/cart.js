// Cart page functionality
function displayCartItems() {
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');
    const checkoutBtn = document.getElementById('checkoutBtn');

    if (!cartItemsContainer) return;

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-shopping-cart text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-500">Your cart is empty</p>
                <a href="index.html" class="btn btn-primary mt-4">Continue Shopping</a>
            </div>
        `;
        if (cartTotalElement) cartTotalElement.textContent = 'Total: $0.00';
        if (checkoutBtn) checkoutBtn.disabled = true;
        return;
    }

    cartItemsContainer.innerHTML = cart.map(item => `
        <div class="card bg-base-100 shadow-sm mb-4">
            <div class="card-body">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                            <i class="fas fa-pills text-2xl text-green-600"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold">${item.name}</h3>
                            <p class="text-green-600 font-bold">${formatPrice(item.price)}</p>
                            <p class="text-sm text-gray-500">${item.manufacturer || ''}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-2">
                            <button class="btn btn-sm btn-outline" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                            <span class="px-3">${item.quantity}</span>
                            <button class="btn btn-sm btn-outline" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        </div>
                        <button class="btn btn-sm btn-error" onclick="removeFromCart(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    if (cartTotalElement) cartTotalElement.textContent = `Total: ${formatPrice(total)}`;
    if (checkoutBtn) checkoutBtn.disabled = false;
}

function updateQuantity(productId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCart(productId);
        return;
    }

    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = newQuantity;
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCount();
        displayCartItems();
    }
}

function clearCart() {
    cart = [];
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    displayCartItems();
    showToast('Cart cleared!', 'info');
}

async function checkout() {
    if (!currentUser) {
        showToast('Please login to checkout', 'error');
        window.location.href = 'login.html';
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const orderData = {
            items: cart.map(item => ({
                medicine_id: item.id,
                quantity: item.quantity
            })),
            shipping_address: "User address" // You can get this from a form
        };

        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            const result = await response.json();
            clearCart();
            showToast('Order placed successfully!', 'success');
            // Redirect to order confirmation page
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        } else {
            throw new Error('Failed to place order');
        }
    } catch (error) {
        showToast('Failed to place order. Please try again.', 'error');
    }
}

// Initialize cart page
if (document.getElementById('cartItems')) {
    document.addEventListener('DOMContentLoaded', function() {
        displayCartItems();
        updateAuthUI();
    });
}