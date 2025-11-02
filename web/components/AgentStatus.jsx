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
        <div className="flex gap-3 mb-6 animate-in slide-in-from-bottom-2 duration-300">
            <Avatar className="h-8 w-8 mt-1 ring-2 ring-background shadow-sm">
                <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                </AvatarFallback>
            </Avatar>

            <Card className="bg-muted/80 shadow-sm border-0">
                <CardContent className="p-3">
                    {type === 'thinking' && (
                        <div className="flex items-center space-x-2">
                            <Brain className="h-4 w-4 text-purple-500 animate-pulse" />
                            <span className="text-sm text-muted-foreground">
                                Thinking... {reasoningTokens && `(${reasoningTokens} tokens)`}
                            </span>
                        </div>
                    )}

                    {type === 'tool_call' && toolCalls && (
                        <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                                <Wrench className="h-4 w-4 text-blue-500" />
                                <span className="text-sm font-medium text-muted-foreground">
                                    Using tools...
                                </span>
                            </div>
                            <div className="space-y-1.5 ml-6">
                                {toolCalls.map((tool, index) => (
                                    <div key={index} className="flex items-center space-x-2">
                                        <Loader2 className="h-3 w-3 text-blue-500 animate-spin flex-shrink-0" />
                                        <span className="text-sm font-medium text-foreground">
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
