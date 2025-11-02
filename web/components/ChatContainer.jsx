'use client';

import { useRef, useEffect, useState } from "react";
import { Card } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";

import ChatHeader from "./ChatHeader";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import { useChat } from "@/hooks/useChat";

export default function ChatContainer() {
    const { t } = useLanguage();
    const { messages, isLoading, sendMessage, agentStatus, thinkingContent }  = useChat();
    const messagesEndRef                        = useRef(null);
    const [isScrolledToBottom, setIsScrolledToBottom] = useState(true);
    const viewportRef                           = useRef(null);

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
        <div className="w-full max-w-5xl mx-auto px-4">
            <Card className={cn(
                "flex flex-col overflow-hidden",
                "h-[85vh] min-h-[600px] max-h-[900px]",
                "bg-card/95 backdrop-blur-sm border-border/50",
                "shadow-2xl shadow-black/10",
                "transition-all duration-300 ease-in-out",
                "hover:shadow-2xl hover:shadow-black/15",
                "relative group"
            )}>
                <div className="absolute inset-0 bg-gradient-to-br from-background/5 via-transparent to-muted/5 pointer-events-none rounded-xl" />
                
                <div className="relative z-10 border-b border-border/50 bg-background/80 backdrop-blur-sm">
                    <ChatHeader />
                </div>
                
                <div className="flex-1 flex flex-col min-h-0 relative z-10">
                    <div className="flex-1 relative overflow-hidden">
                        <ScrollArea className="h-full w-full">
                            <div className="p-6 pb-4">
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