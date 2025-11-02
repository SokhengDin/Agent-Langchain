'use client';

import { createContext, useContext, useState, useEffect } from 'react';

import enLocale from '@/locales/en.json';
import kmLocale from '@/locales/km.json';

const locales = {
    en: enLocale,
    km: kmLocale
};

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
    const [currentLanguage, setCurrentLanguage] = useState('km');
    const [translations, setTranslations]       = useState(locales.km);

    useEffect(() => {
        const savedLanguage = localStorage.getItem('chat-language');
        if (savedLanguage && locales[savedLanguage]) {
            setCurrentLanguage(savedLanguage);
            setTranslations(locales[savedLanguage]);
        }
    }, []);

    useEffect(() => {
        if (typeof document !== 'undefined') {
            document.documentElement.lang = currentLanguage === 'km' ? 'km-KH' : 'en-US';
        }
    }, [currentLanguage]);

    const switchLanguage    = (language) => {
        if (locales[language]) {
            setCurrentLanguage(language);
            setTranslations(locales[language]);
            localStorage.setItem('chat-language', language);
        }
    };

    const t = (key) => {
        const keys  = key.split('.');
        let value   = translations;
        
        for (const k of keys) {
            value = value?.[k];
            if (value === undefined) {
                console.warn(`Translation key "${key}" not found`);
                return key;
            }
        }
        
        return value;
    };

    const value = {
        currentLanguage,
        switchLanguage,
        t,
        availableLanguages: Object.keys(locales)
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
} 