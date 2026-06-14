const API_BASE_URL = 'http://localhost:8080';

const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
};

export const login = async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    if (!response.ok) throw new Error('Login failed');
    return response.text(); // token JWT
};

export const register = async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    if (!response.ok) throw new Error('Registration failed');
    return response.json();
};

export const getHomeRecommendations = async () => {
    const response = await fetch(`${API_BASE_URL}/home`, {
        headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    return response.json();
};

export const getProduct = async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
        headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch product');
    return response.json();
};

export const getProductRecommendations = async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}/recommendations`, {
        headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    return response.json();
};

export const searchProducts = async (query) => {
    const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`, {
        headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Search failed');
    return response.json();
};
