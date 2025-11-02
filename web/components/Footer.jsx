'use client';

import { useLanguage } from '@/contexts/LanguageContext';

export default function Footer() {
  const { t } = useLanguage();
  
  return (
    <div className="text-center mt-8 text-sm text-muted-foreground">
      <p>{t('footer.developedBy')}</p>
    </div>
  );
} 