'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Brain, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function ThinkingIndicatorSticky({ thinkingContent }) {
    const [dots, setDots] = useState('');

    // Animate the dots
    useEffect(() => {
        const interval = setInterval(() => {
            setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
        }, 500);
        return () => clearInterval(interval);
    }, []);

    return (
        <Card className="bg-gradient-to-br from-primary/10 via-primary/5 to-background border border-primary/30 shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom-2 duration-500 ease-out">
            <CardContent className="p-3 sm:p-4">
                <div className="space-y-2">
                    {/* Thinking Header */}
                    <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 text-primary">
                            <Brain className="h-4 w-4 sm:h-5 sm:w-5 animate-pulse flex-shrink-0" />
                            <span className="text-xs sm:text-sm font-semibold">
                                AI is thinking{dots}
                            </span>
                            <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4 animate-pulse flex-shrink-0" />
                        </div>

                        {/* Animated thinking dots */}
                        <div className="flex gap-1">
                            <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                    </div>

                    {/* Thinking Content - shown if available */}
                    {thinkingContent && (
                        <div className="pt-2 border-t border-primary/20">
                            <div className="text-xs sm:text-sm text-muted-foreground italic font-mono bg-background/80 rounded-md px-2 sm:px-3 py-2 max-h-24 sm:max-h-32 overflow-y-auto break-words shadow-inner">
                                <span className="opacity-70">&quot;</span>
                                <span className="text-foreground/80">{thinkingContent}</span>
                                <span className="inline-block w-1 h-3 sm:h-3.5 bg-primary/70 animate-pulse ml-0.5"></span>
                                <span className="opacity-70">&quot;</span>
                            </div>
                        </div>
                    )}

                    {/* Processing status */}
                    <div className="flex items-center justify-center pt-1">
                        <span className="text-[10px] sm:text-xs text-muted-foreground/80">
                            Processing your request...
                        </span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
