'use client';

import { useRef, useEffect, useState } from "react";
import { Card } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";
import { BrainCircuit, Hotel } from "lucide-react";

import ChatHeader from "./ChatHeader";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import { useChat } from "@/hooks/useChat";
import { useDSChat } from "@/hooks/useDSChat";

export default function ChatContainer() {
    const { t } = useLanguage();

    // Agent type state - default to 'ds-agent'
    const [activeAgent, setActiveAgent] = useState('ds-agent');

    // Hooks for both agents
    const hotelChat = useChat();
    const dsChat = useDSChat();

    // Select the active chat based on agent type
    const { messages, isLoading, sendMessage, agentStatus, thinkingContent } =
        activeAgent === 'ds-agent' ? dsChat : hotelChat;

    const messagesEndRef = useRef(null);
    const [isScrolledToBottom, setIsScrolledToBottom] = useState(true);
    const viewportRef = useRef(null);

    const scrollToBottom    = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth'});
    };

    useEffect(() => {
        if (isScrolledToBottom) {
            scrollToBottom();
        }
    }, [messages, agentStatus, isScrolledToBottom]);

    useEffect(() => {
        // Find the viewport element (Radix UI ScrollArea creates it)
        const findViewport = () => {
            const scrollArea = document.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollArea) {
                viewportRef.current = scrollArea;

                const handleScroll = () => {
                    const { scrollTop, scrollHeight, clientHeight } = scrollArea;
                    const isAtBottom = scrollHeight - scrollTop <= clientHeight + 50;
                    setIsScrolledToBottom(isAtBottom);
                };

                scrollArea.addEventListener('scroll', handleScroll);
                return () => scrollArea.removeEventListener('scroll', handleScroll);
            }
        };

        // Small delay to ensure DOM is ready
        const timer = setTimeout(findViewport, 100);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Card className={cn(
                "flex flex-col overflow-hidden",
                "h-[90vh] min-h-[700px] max-h-[1200px]",
                "bg-card/95 backdrop-blur-sm border-border/50",
                "shadow-2xl shadow-black/10",
                "transition-all duration-300 ease-in-out",
                "hover:shadow-2xl hover:shadow-black/15",
                "relative group"
            )}>
                <div className="absolute inset-0 bg-gradient-to-br from-background/5 via-transparent to-muted/5 pointer-events-none rounded-xl" />

                <div className="relative z-10 border-b border-border/50 bg-background/80 backdrop-blur-sm">
                    <ChatHeader activeAgent={activeAgent} />

                    {/* Agent Tabs */}
                    <div className="px-4 pb-3">
                        <Tabs value={activeAgent} onValueChange={setActiveAgent} className="w-full">
                            <TabsList className="grid w-full grid-cols-2 h-11">
                                <TabsTrigger
                                    value="ds-agent"
                                    className="flex items-center gap-2 text-xs sm:text-sm"
                                >
                                    <BrainCircuit className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                                    <span className="hidden sm:inline">{t('chat.dsAgent')}</span>
                                    <span className="sm:hidden">{t('chat.dsAgentShort')}</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="hotel-agent"
                                    className="flex items-center gap-2 text-xs sm:text-sm"
                                >
                                    <Hotel className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                                    <span className="hidden sm:inline">{t('chat.hotelAgent')}</span>
                                    <span className="sm:hidden">{t('chat.hotelAgentShort')}</span>
                                </TabsTrigger>
                            </TabsList>
                        </Tabs>
                    </div>
                </div>
                
                <div className="flex-1 flex flex-col min-h-0 relative z-10">
                    <div className="flex-1 relative overflow-hidden">
                        <ScrollArea className="h-full w-full">
                            <div className="px-6 sm:px-8 md:px-12 py-6 sm:py-8">
                                <ChatMessages messages={messages} isLoading={isLoading} agentStatus={agentStatus} thinkingContent={thinkingContent} />
                                <div ref={messagesEndRef} />
                            </div>
                        </ScrollArea>
                        
                        {!isScrolledToBottom && messages.length > 0 && (
                            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
                                <button
                                    onClick={scrollToBottom}
                                    className={cn(
                                        "flex items-center gap-2 px-3 py-2 rounded-full",
                                        "bg-primary/90 text-primary-foreground text-sm font-medium",
                                        "shadow-lg backdrop-blur-sm border border-primary/20",
                                        "hover:bg-primary hover:scale-105 active:scale-95",
                                        "transition-all duration-200 ease-in-out",
                                        "animate-in slide-in-from-bottom-2 fade-in-0"
                                    )}
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                                    </svg>
                                                                         {t('chat.newMessages')}
                                </button>
                            </div>
                        )}
                        
                        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-background/80 to-transparent pointer-events-none" />
                    </div>
                    
                    <div className="border-t border-border/50 bg-background/80 backdrop-blur-sm">
                        <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
                    </div>
                </div>
            </Card>
        </div>
    );
}