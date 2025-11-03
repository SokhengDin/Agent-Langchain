'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import AgentStatus from './AgentStatus';
import ThinkingIndicator from './ThinkingIndicator';
import { FileText, Image as ImageIcon } from 'lucide-react';

function MessageBubble({ message }) {
    const [mounted, setMounted] = useState(false);
    const isUser    = message.sender === 'user';
    const isError   = message.isError;

    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <div className={cn(
            "flex gap-2 sm:gap-3 mb-4 sm:mb-6 animate-in slide-in-from-bottom-2 duration-300",
            isUser ? "flex-row-reverse" : "flex-row"
        )}>
            <Avatar className="h-7 w-7 sm:h-8 sm:w-8 mt-1 ring-2 ring-background shadow-sm flex-shrink-0">
                {isUser ? (
                    <>
                        <AvatarImage src="/user-avatar.png" alt="User" />
                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                            <User className='h-3.5 w-3.5 sm:h-4 sm:w-4' />
                        </AvatarFallback>
                    </>
                ) : (
                    <>
                        <AvatarImage src="/agent-avatar.png" alt="AI Agent" />
                        <AvatarFallback className="bg-primary text-primary-foreground">
                            <Bot className='h-3.5 w-3.5 sm:h-4 sm:w-4' />
                        </AvatarFallback>
                    </>
                )}
            </Avatar>

            <div className={cn(
                "flex flex-col max-w-[85%] sm:max-w-[80%] md:max-w-[75%] min-w-0",
                isUser ? "items-end" : "items-start"
            )}>
                <Card className={cn(
                    "inline-block shadow-sm border-0 w-full sm:w-auto",
                    isUser
                    ? "bg-primary text-primary-foreground"
                    : isError
                        ? "bg-destructive/10 border-destructive/20"
                        : "bg-muted/80"
                )}>
                    <CardContent className="p-2.5 sm:p-3">
                        {/* Show attachments if present */}
                        {message.attachments && message.attachments.length > 0 && (
                            <div className="mb-2 space-y-1.5 sm:space-y-2">
                                {message.attachments.map((att, idx) => (
                                    <div key={idx} className={cn(
                                        "flex items-center gap-1.5 sm:gap-2 p-1.5 sm:p-2 rounded-md min-w-0",
                                        isUser ? "bg-primary-foreground/10" : "bg-background/50"
                                    )}>
                                        {att.type.startsWith('image/') ? (
                                            <>
                                                <ImageIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 flex-shrink-0" />
                                                <span className="text-xs truncate min-w-0">{att.name}</span>
                                            </>
                                        ) : (
                                            <>
                                                <FileText className="h-3.5 w-3.5 sm:h-4 sm:w-4 flex-shrink-0" />
                                                <span className="text-xs truncate min-w-0">{att.name}</span>
                                            </>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                        {isUser ? (
                            <p className='text-xs sm:text-sm whitespace-pre-wrap leading-relaxed m-0 break-words'>{message.content}</p>
                        ) : (
                            <div className='text-xs sm:text-sm leading-relaxed prose prose-sm max-w-none dark:prose-invert min-w-0'>
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        p: ({node, ...props}) => <p className='mb-2 last:mb-0 break-words' {...props} />,
                                        ul: ({node, ...props}) => <ul className='mb-2 ml-3 sm:ml-4 list-disc' {...props} />,
                                        ol: ({node, ...props}) => <ol className='mb-2 ml-3 sm:ml-4 list-decimal' {...props} />,
                                        li: ({node, ...props}) => <li className='mb-1 break-words' {...props} />,
                                        code: ({node, inline, ...props}) =>
                                            inline ? (
                                                <code className='bg-muted px-1 py-0.5 rounded text-[11px] sm:text-xs font-mono break-all' {...props} />
                                            ) : (
                                                <code className='block bg-muted p-2 sm:p-3 rounded-md text-[11px] sm:text-xs font-mono overflow-x-auto my-2 max-w-full' {...props} />
                                            ),
                                        pre: ({node, ...props}) => <pre className='bg-muted rounded-md overflow-x-auto my-2 max-w-full' {...props} />,
                                        h1: ({node, ...props}) => <h1 className='text-base sm:text-lg font-bold mb-2 mt-4 first:mt-0 break-words' {...props} />,
                                        h2: ({node, ...props}) => <h2 className='text-sm sm:text-base font-bold mb-2 mt-3 first:mt-0 break-words' {...props} />,
                                        h3: ({node, ...props}) => <h3 className='text-xs sm:text-sm font-bold mb-1 mt-2 first:mt-0 break-words' {...props} />,
                                        a: ({node, ...props}) => <a className='text-primary underline hover:text-primary/80 break-all' {...props} target="_blank" rel="noopener noreferrer" />,
                                        blockquote: ({node, ...props}) => <blockquote className='border-l-2 sm:border-l-4 border-muted-foreground/20 pl-2 sm:pl-4 italic my-2' {...props} />,
                                        table: ({node, ...props}) => (
                                            <div className='overflow-x-auto my-2 -mx-1 sm:mx-0'>
                                                <table className='border-collapse border border-muted min-w-full' {...props} />
                                            </div>
                                        ),
                                        th: ({node, ...props}) => <th className='border border-muted px-1.5 sm:px-2 py-1 bg-muted/50 font-semibold text-xs sm:text-sm' {...props} />,
                                        td: ({node, ...props}) => <td className='border border-muted px-1.5 sm:px-2 py-1 text-xs sm:text-sm' {...props} />,
                                        hr: ({node, ...props}) => <hr className='my-2 sm:my-3 border-muted' {...props} />,
                                    }}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            </div>
                        )}
                    </CardContent>
                </Card>
                <span className='text-[10px] sm:text-xs text-muted-foreground mt-1 px-1'>
                    {mounted ? new Date(message.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    }) : ''}
                </span>
            </div>
        </div>
    );
}

function TypingIndicator() {
    return (
      <div className="flex gap-2 sm:gap-3 mb-4 sm:mb-6 animate-in slide-in-from-bottom-2 duration-300">
        <Avatar className="h-7 w-7 sm:h-8 sm:w-8 mt-1 ring-2 ring-background shadow-sm flex-shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground">
                <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
            </AvatarFallback>
        </Avatar>
        <Card className="bg-muted/80 shadow-sm border-0">
            <CardContent className="p-2.5 sm:p-3">
                <div className="flex items-center space-x-2">
                    <Loader2 className="h-3.5 w-3.5 sm:h-4 sm:w-4 animate-spin text-primary" />
                    <span className="text-xs sm:text-sm text-muted-foreground">AI is typing...</span>
                </div>
            </CardContent>
        </Card>
      </div>
    );
}

export default function ChatMessages({ messages, isLoading, agentStatus, thinkingContent }) {
    // Check if there's a streaming message
    const hasStreamingMessage = messages.some(msg => msg.isStreaming);

    // Only show typing indicator if loading but no message is streaming yet and not thinking
    const showTypingIndicator = isLoading && !hasStreamingMessage && !agentStatus;

    // Check if agent is thinking
    const isThinking = agentStatus && agentStatus.type === 'thinking';

    return (
        <div className='space-y-1'>
            {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
            ))}
            {isThinking ? (
                <ThinkingIndicator thinkingContent={thinkingContent} />
            ) : agentStatus ? (
                <AgentStatus status={agentStatus} />
            ) : showTypingIndicator ? (
                <TypingIndicator />
            ) : null}
        </div>
    )
}