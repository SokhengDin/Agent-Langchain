'use client';

import ChatContainer from "@/components/ChatContainer";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AuthProvider } from "@/contexts/AuthContext";
import Footer from "@/components/Footer";
import WelcomeModal from "@/components/WelcomeModal";

export default function Home() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
          <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

          <div className="relative container mx-auto py-8 px-4">
            <ChatContainer />
            <Footer />
          </div>

          <WelcomeModal />
        </div>
      </AuthProvider>
    </LanguageProvider>
  )
}