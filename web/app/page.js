'use client';

import ChatContainer from "@/components/ChatContainer";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AuthProvider } from "@/contexts/AuthContext";
import WelcomeModal from "@/components/WelcomeModal";

export default function Home() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 overflow-x-hidden">
          <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

          <div className="relative container mx-auto pt-4 sm:pt-8 pb-2 sm:pb-4 px-2 sm:px-4 max-w-full">
            <ChatContainer />
          </div>

          <WelcomeModal />
        </div>
      </AuthProvider>
    </LanguageProvider>
  )
}