'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, Brain, Sparkles } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

export default function ThinkingIndicator({ thinkingContent }) {
    const [dots, setDots] = useState('');
    const contentRef = useRef(null);

    // Animate the dots
    useEffect(() => {
        const interval = setInterval(() => {
            setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
        }, 500);
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll to bottom when content updates
    useEffect(() => {
        if (contentRef.current && thinkingContent) {
            // Small delay to ensure content is rendered
            requestAnimationFrame(() => {
                if (contentRef.current) {
                    contentRef.current.scrollTop = contentRef.current.scrollHeight;
                }
            });
        }
    }, [thinkingContent]);

    return (
        <div className="flex gap-2 sm:gap-3 mb-4 sm:mb-6 animate-in slide-in-from-bottom-2 duration-300">
            <Avatar className="h-7 w-7 sm:h-8 sm:w-8 mt-1 ring-2 ring-background shadow-sm flex-shrink-0">
                <AvatarImage src="/agent-avatar.png" alt="AI Agent" />
                <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                </AvatarFallback>
            </Avatar>

            <div className="flex flex-col max-w-[85%] sm:max-w-[80%] md:max-w-[75%] min-w-0">
                <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 shadow-sm">
                    <CardContent className="p-2.5 sm:p-3">
                        <div className="space-y-1.5 sm:space-y-2">
                            {/* Thinking Header */}
                            <div className="flex items-center gap-1.5 sm:gap-2 text-primary">
                                <Brain className="h-3.5 w-3.5 sm:h-4 sm:w-4 animate-pulse flex-shrink-0" />
                                <span className="text-[11px] sm:text-xs font-medium">
                                    AI is thinking{dots}
                                </span>
                                <Sparkles className="h-3 w-3 animate-pulse flex-shrink-0" />
                            </div>

                            {/* Thinking Content - shown if available */}
                            {thinkingContent && (
                                <div className="mt-1.5 sm:mt-2 pt-1.5 sm:pt-2 border-t border-primary/10 animate-in fade-in duration-300">
                                    <div
                                        ref={contentRef}
                                        className="text-[11px] sm:text-xs text-muted-foreground italic font-mono bg-background/50 rounded px-1.5 sm:px-2 py-1 sm:py-1.5 max-h-24 sm:max-h-32 overflow-y-auto break-words smooth-scroll"
                                    >
                                        <span className="opacity-70">&quot;</span>
                                        <span className="text-foreground/70 thinking-text">{thinkingContent}</span>
                                        <span className="inline-block w-1 h-2.5 sm:h-3 bg-primary/60 ml-0.5 cursor-blink"></span>
                                        <span className="opacity-70">&quot;</span>
                                    </div>
                                </div>
                            )}

                            {/* Animated thinking indicator */}
                            <div className="flex items-center gap-1 mt-1.5 sm:mt-2">
                                <div className="flex gap-1">
                                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                                <span className="text-[10px] text-muted-foreground ml-1.5 sm:ml-2">
                                    Processing your request
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
