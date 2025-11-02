'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home, MessageCircle } from 'lucide-react';
import { LanguageProvider, useLanguage } from '@/contexts/LanguageContext';

function NotFoundContent() {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="relative z-10 text-center space-y-8">
        {/* Big 404 */}
        <div className="space-y-4">
          <h1 className="text-9xl font-bold text-primary/30 select-none animate-pulse">
            404
          </h1>
          <h2 className="text-2xl font-semibold text-foreground">
            {t('notFound.title')}
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            {t('notFound.description')}
          </p>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/" className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              {t('notFound.backToChat')}
            </Link>
          </Button>
          
          <Button variant="outline" size="lg" onClick={() => history.back()}>
            <Home className="w-5 h-5 mr-2" />
            {t('notFound.goBack')}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function NotFound() {
  return (
    <LanguageProvider>
      <NotFoundContent />
    </LanguageProvider>
  );
} 