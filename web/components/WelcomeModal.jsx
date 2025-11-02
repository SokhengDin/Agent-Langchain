'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { X, Bot, Users, GraduationCap, ExternalLink, Loader2 } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { handleApiResponse, logAndGetUserMessage } from '@/lib/apiErrorHandler';
import Image from 'next/image';
import Link from 'next/link';

export default function WelcomeModal() {
    const { t } = useLanguage();
    const { showAuthModal, setShowAuthModal, login } = useAuth();
    const [view, setView] = useState('welcome'); // 'welcome', 'login', 'register'
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Form states
    const [loginData, setLoginData] = useState({ email: '', password: '' });
    const [registerData, setRegisterData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        name: ''
    });

    const handleClose = () => {
        setShowAuthModal(false);
        localStorage.setItem('ams-chat-welcome-seen', 'true');
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(loginData),
            });

            const data = await handleApiResponse(response, 'login');

            // Store the access token
            if (data.data?.access_token) {
                login(data.data.access_token, data.data?.user);
                handleClose();
            } else {
                throw new Error('No access token received from server');
            }
        } catch (err) {
            const userMessage = logAndGetUserMessage(err, 'Login');
            setError(userMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');

        if (registerData.password !== registerData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: registerData.email,
                    password: registerData.password,
                    name: registerData.name,
                }),
            });

            const data = await handleApiResponse(response, 'registration');

            // Store the access token if registration returns one
            if (data.data?.access_token) {
                login(data.data.access_token, data.data?.user);
                handleClose();
            } else {
                // If no token, switch to login view
                setView('login');
                setError('Registration successful! Please login with your credentials.');
            }
        } catch (err) {
            const userMessage = logAndGetUserMessage(err, 'Registration');
            setError(userMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSkip = () => {
        handleClose();
    };

    if (!showAuthModal) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={handleClose}
            />

            {/* Modal */}
            <Card className="relative w-full max-w-md bg-background border-border shadow-2xl animate-in zoom-in-95 duration-300">
                {/* Close Button */}
                <button
                    onClick={handleClose}
                    className="absolute top-4 right-4 p-1 rounded-full hover:bg-muted/80 transition-colors z-10"
                >
                    <X className="h-4 w-4 text-muted-foreground" />
                </button>

                <div className="p-6">
                    {/* Logo */}
                    <div className="flex justify-center mb-6">
                        <div className="relative w-32 h-20">
                            <Image
                                src="/logo/logo.jpg"
                                alt="AMS Department Logo"
                                fill
                                className="object-contain"
                                priority
                            />
                        </div>
                    </div>

                    {/* Welcome View */}
                    {view === 'welcome' && (
                        <div className="text-center space-y-6">
                            <div className="space-y-2">
                                <h2 className="text-2xl font-bold text-foreground">
                                    {t('welcome.title')}
                                </h2>
                                <p className="text-sm text-muted-foreground">
                                    {t('welcome.subtitle')}
                                </p>
                                <Link
                                    href="https://itc.edu.kh/home-ams/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
                                >
                                    {t('welcome.visitDepartment')}
                                    <ExternalLink className="w-3 h-3" />
                                </Link>
                            </div>

                            <div className="space-y-3">
                                <div className="flex items-center gap-3 text-left">
                                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">{t('welcome.feature1')}</p>
                                        <p className="text-xs text-muted-foreground">{t('welcome.feature1Desc')}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 text-left">
                                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                        <Users className="w-4 h-4 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">{t('welcome.feature2')}</p>
                                        <p className="text-xs text-muted-foreground">{t('welcome.feature2Desc')}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 text-left">
                                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                        <GraduationCap className="w-4 h-4 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">{t('welcome.feature3')}</p>
                                        <p className="text-xs text-muted-foreground">{t('welcome.feature3Desc')}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <Button
                                    onClick={() => setView('login')}
                                    className="w-full"
                                    size="lg"
                                >
                                    Login
                                </Button>

                                <Button
                                    onClick={() => setView('register')}
                                    variant="outline"
                                    className="w-full"
                                    size="lg"
                                >
                                    Register
                                </Button>

                                <Button
                                    onClick={handleSkip}
                                    variant="ghost"
                                    className="w-full text-xs"
                                    size="sm"
                                >
                                    Skip for now
                                </Button>
                            </div>

                            <p className="text-xs text-muted-foreground/70">
                                {t('welcome.note')}
                            </p>
                        </div>
                    )}

                    {/* Login View */}
                    {view === 'login' && (
                        <div className="space-y-6">
                            <div className="text-center space-y-2">
                                <h2 className="text-2xl font-bold text-foreground">
                                    Welcome Back
                                </h2>
                                <p className="text-sm text-muted-foreground">
                                    Sign in to continue chatting
                                </p>
                            </div>

                            {error && (
                                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                                    <p className="text-sm text-destructive">{error}</p>
                                </div>
                            )}

                            <form onSubmit={handleLogin} className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-foreground">
                                        Email
                                    </label>
                                    <Input
                                        type="email"
                                        placeholder="Enter your email"
                                        value={loginData.email}
                                        onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-foreground">
                                        Password
                                    </label>
                                    <Input
                                        type="password"
                                        placeholder="Enter your password"
                                        value={loginData.password}
                                        onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full"
                                    size="lg"
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Logging in...
                                        </>
                                    ) : (
                                        'Login'
                                    )}
                                </Button>

                                <div className="text-center">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setView('register');
                                            setError('');
                                        }}
                                        className="text-sm text-primary hover:text-primary/80 transition-colors"
                                    >
                                        Don't have an account? Register
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    {/* Register View */}
                    {view === 'register' && (
                        <div className="space-y-6">
                            <div className="text-center space-y-2">
                                <h2 className="text-2xl font-bold text-foreground">
                                    Create Account
                                </h2>
                                <p className="text-sm text-muted-foreground">
                                    Sign up to start chatting
                                </p>
                            </div>

                            {error && (
                                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                                    <p className="text-sm text-destructive">{error}</p>
                                </div>
                            )}

                            <form onSubmit={handleRegister} className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-foreground">
                                        Name
                                    </label>
                                    <Input
                                        type="text"
                                        placeholder="Enter your name"
                                        value={registerData.name}
                                        onChange={(e) => setRegisterData({ ...registerData, name: e.target.value })}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-foreground">
                                        Email
                                    </label>
                                    <Input
                                        type="email"
                                        placeholder="Enter your email"
                                        value={registerData.email}
                                        onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-foreground">
                                        Password
                                    </label>
                                    <Input
                                        type="password"
                                        placeholder="Create a password"
                                        value={registerData.password}
                                        onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-foreground">
                                        Confirm Password
                                    </label>
                                    <Input
                                        type="password"
                                        placeholder="Confirm your password"
                                        value={registerData.confirmPassword}
                                        onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full"
                                    size="lg"
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Registering...
                                        </>
                                    ) : (
                                        'Register'
                                    )}
                                </Button>

                                <div className="text-center">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setView('login');
                                            setError('');
                                        }}
                                        className="text-sm text-primary hover:text-primary/80 transition-colors"
                                    >
                                        Already have an account? Login
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
}
