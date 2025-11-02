'use client';

import { Languages } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/LanguageContext';

export default function LanguageToggle() {
    const { currentLanguage, switchLanguage } = useLanguage();

    const handleToggle = () => {
        const newLang = currentLanguage === 'en' ? 'km' : 'en';
        console.log(`Switching from ${currentLanguage} to ${newLang}`);
        switchLanguage(newLang);
    };

    const getCurrentFlag = () => {
        return currentLanguage === 'en' ? '🇺🇸' : '🇰🇭';
    };

    const getCurrentName = () => {
        return currentLanguage === 'en' ? 'English' : 'ខ្មែរ';
    };

    return (
        <button
            onClick={handleToggle}
            className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-md",
                "text-sm font-medium transition-all duration-200",
                "hover:bg-muted/80 active:bg-muted",
                "border border-transparent hover:border-border/50",
                "focus:outline-none focus:ring-2 focus:ring-primary/20",
                "cursor-pointer select-none"
            )}
            title={`Switch to ${currentLanguage === 'en' ? 'Khmer' : 'English'}`}
        >
            <Languages className="h-4 w-4" />
            <span>{getCurrentFlag()} {getCurrentName()}</span>
        </button>
    );
} 