'use client';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, Wrench, Brain, Loader2 } from 'lucide-react';

// Helper to format tool names into readable text
const formatToolName = (toolName) => {
    return toolName
        .replace(/_tool$/, '')
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
};

export default function AgentStatus({ status }) {
    if (!status) return null;

    const { type, toolCalls, reasoningTokens } = status;

    return (
        <div className="flex gap-2 sm:gap-3 mb-4 sm:mb-6 animate-in slide-in-from-bottom-2 duration-300">
            <Avatar className="h-7 w-7 sm:h-8 sm:w-8 mt-1 ring-2 ring-background shadow-sm flex-shrink-0">
                <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                </AvatarFallback>
            </Avatar>

            <Card className="bg-muted/80 shadow-sm border-0">
                <CardContent className="p-2.5 sm:p-3">
                    {type === 'thinking' && (
                        <div className="flex items-center space-x-2">
                            <Brain className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-purple-500 animate-pulse flex-shrink-0" />
                            <span className="text-xs sm:text-sm text-muted-foreground">
                                Thinking... {reasoningTokens && `(${reasoningTokens} tokens)`}
                            </span>
                        </div>
                    )}

                    {type === 'tool_call' && toolCalls && (
                        <div className="space-y-1.5 sm:space-y-2">
                            <div className="flex items-center space-x-2">
                                <Wrench className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-500 flex-shrink-0" />
                                <span className="text-xs sm:text-sm font-medium text-muted-foreground">
                                    Using tools...
                                </span>
                            </div>
                            <div className="space-y-1 sm:space-y-1.5 ml-5 sm:ml-6">
                                {toolCalls.map((tool, index) => (
                                    <div key={index} className="flex items-center space-x-1.5 sm:space-x-2">
                                        <Loader2 className="h-3 w-3 text-blue-500 animate-spin flex-shrink-0" />
                                        <span className="text-xs sm:text-sm font-medium text-foreground break-words">
                                            {formatToolName(tool.name)}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
