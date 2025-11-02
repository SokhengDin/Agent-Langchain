'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, Brain, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';

export default function ThinkingIndicator({ thinkingContent }) {
    const [dots, setDots] = useState('');

    // Animate the dots
    useEffect(() => {
        const interval = setInterval(() => {
            setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
        }, 500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex gap-3 mb-6 animate-in slide-in-from-bottom-2 duration-300">
            <Avatar className="h-8 w-8 mt-1 ring-2 ring-background shadow-sm">
                <AvatarImage src="/agent-avatar.png" alt="AI Agent" />
                <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                </AvatarFallback>
            </Avatar>

            <div className="flex flex-col max-w-[80%]">
                <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 shadow-sm">
                    <CardContent className="p-3">
                        <div className="space-y-2">
                            {/* Thinking Header */}
                            <div className="flex items-center gap-2 text-primary">
                                <Brain className="h-4 w-4 animate-pulse" />
                                <span className="text-xs font-medium">
                                    AI is thinking{dots}
                                </span>
                                <Sparkles className="h-3 w-3 animate-pulse" />
                            </div>

                            {/* Thinking Content - shown if available */}
                            {thinkingContent && (
                                <div className="mt-2 pt-2 border-t border-primary/10">
                                    <div className="text-xs text-muted-foreground italic font-mono bg-background/50 rounded px-2 py-1.5 max-h-32 overflow-y-auto">
                                        <span className="opacity-70">&quot;</span>
                                        <span className="text-foreground/70">{thinkingContent}</span>
                                        <span className="inline-block w-1 h-3 bg-primary/60 animate-pulse ml-0.5"></span>
                                        <span className="opacity-70">&quot;</span>
                                    </div>
                                </div>
                            )}

                            {/* Animated thinking indicator */}
                            <div className="flex items-center gap-1 mt-2">
                                <div className="flex gap-1">
                                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                                <span className="text-[10px] text-muted-foreground ml-2">
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
