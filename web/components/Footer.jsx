'use client';

import { useLanguage } from '@/contexts/LanguageContext';

export default function Footer() {
  const { t } = useLanguage();
  
  return (
    <div className="text-center mt-2 sm:mt-6 text-[10px] sm:text-xs text-muted-foreground/80 py-1 sm:py-2">
      <p>{t('footer.developedBy')}</p>
    </div>
  );
} 