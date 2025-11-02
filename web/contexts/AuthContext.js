'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { authHelpers } from '@/lib/auth';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [user, setUser] = useState(null);

    // Check authentication status on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        const token = authHelpers.getToken();
        const hasSeenModal = localStorage.getItem('ams-chat-welcome-seen');

        if (!token) {
            setIsAuthenticated(false);
            setIsLoading(false);
            // Only show modal if user hasn't seen it before
            if (!hasSeenModal) {
                setShowAuthModal(true);
            }
            return;
        }

        // Verify token with backend
        try {
            const response = await fetch('/api/v1/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const data = await response.json();

            if (response.ok && response.status === 200) {
                setIsAuthenticated(true);
                setUser(data.data);
                setShowAuthModal(false);
            } else {
                // Token is invalid or expired
                handleAuthError();
            }
        } catch (error) {
            console.error('Auth check error:', error);
            handleAuthError();
        } finally {
            setIsLoading(false);
        }
    };

    const handleAuthError = () => {
        authHelpers.clearAuth();
        setIsAuthenticated(false);
        setUser(null);
        setShowAuthModal(true);
    };

    const login = (token, userData = null) => {
        authHelpers.setToken(token);

        if (userData) {
            authHelpers.setUser(userData);
            setUser(userData);
        }
        setIsAuthenticated(true);
        setShowAuthModal(false);
    };

    const logout = async () => {
        const token = authHelpers.getToken();

        if (token) {
            try {
                await fetch('/api/v1/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }

        authHelpers.clearAuth();
        setIsAuthenticated(false);
        setUser(null);
        setShowAuthModal(true);
    };

    const value = {
        isAuthenticated,
        isLoading,
        showAuthModal,
        setShowAuthModal,
        user,
        login,
        logout,
        checkAuth,
        handleAuthError,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
