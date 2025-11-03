// Auth helper utilities for managing tokens and user authentication

export const authHelpers = {
    // Get token from localStorage
    getToken: () => {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem('access_token');
    },

    // Store token in localStorage
    setToken: (token) => {
        if (typeof window === 'undefined') return;
        localStorage.setItem('access_token', token);
    },

    // Remove token from localStorage
    removeToken: () => {
        if (typeof window === 'undefined') return;
        localStorage.removeItem('access_token');
    },

    // Check if user is authenticated
    isAuthenticated: () => {
        return !!authHelpers.getToken();
    },

    // Get authorization header
    getAuthHeader: () => {
        const token = authHelpers.getToken();
        return token ? `Bearer ${token}` : null;
    },

    // Store user data
    setUser: (userData) => {
        if (typeof window === 'undefined') return;
        localStorage.setItem('user', JSON.stringify(userData));
    },

    // Get user data
    getUser: () => {
        if (typeof window === 'undefined') return null;
        const userData = localStorage.getItem('user');
        return userData ? JSON.parse(userData) : null;
    },

    // Remove user data
    removeUser: () => {
        if (typeof window === 'undefined') return;
        localStorage.removeItem('user');
    },

    // Clear all auth data
    clearAuth: () => {
        authHelpers.removeToken();
        authHelpers.removeUser();
    },
};
