// Authentication functions
function updateAuthUI() {
    const userSection = document.getElementById('userSection');
    const loggedInSection = document.getElementById('loggedInSection');
    const userProfileLink = document.getElementById('userProfileLink');

    if (currentUser) {
        if (userSection) userSection.classList.add('hidden');
        if (loggedInSection) loggedInSection.classList.remove('hidden');
        if (userProfileLink) {
            userProfileLink.textContent = `Hello, ${currentUser.name}`;
        }
    } else {
        if (userSection) userSection.classList.remove('hidden');
        if (loggedInSection) loggedInSection.classList.add('hidden');
    }
}

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            localStorage.setItem('token', data.token);
            updateAuthUI();
            showToast('Login successful!', 'success');
            return { success: true, message: 'Login successful' };
        } else {
            return { success: false, message: data.detail || 'Login failed' };
        }
    } catch (error) {
        return { success: false, message: 'Network error. Please try again.' };
    }
}

async function register(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        const data = await response.json();
        
        if (response.ok) {
            showToast('Registration successful!', 'success');
            return { success: true, message: 'Registration successful' };
        } else {
            return { success: false, message: data.detail || 'Registration failed' };
        }
    } catch (error) {
        return { success: false, message: 'Network error. Please try again.' };
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    localStorage.removeItem('token');
    updateAuthUI();
    showToast('Logged out successfully!', 'info');
    window.location.href = 'index.html';
}

// Login form handler
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const submitBtn = document.getElementById('loginBtn');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Logging in...';
        
        const result = await login(email, password);
        
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
        
        if (result.success) {
            window.location.href = 'index.html';
        } else {
            showToast(result.message, 'error');
        }
    });
}

// Registration form handler
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            phone: document.getElementById('phone').value,
            address: document.getElementById('address').value
        };
        
        const submitBtn = document.getElementById('registerBtn');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Registering...';
        
        const result = await register(formData);
        
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
        
        if (result.success) {
            window.location.href = 'login.html';
        } else {
            showToast(result.message, 'error');
        }
    });
}