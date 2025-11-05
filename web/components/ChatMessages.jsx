'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { codeToHtml } from 'shiki';
import AgentStatus from './AgentStatus';
import 'katex/dist/katex.min.css';
import ThinkingIndicator from './ThinkingIndicator';
import { FileText, Image as ImageIcon } from 'lucide-react';
// @ts-ignore - KaTeX auto-render types not available
import renderMathInElement from 'katex/dist/contrib/auto-render.mjs';

/**
 * KaTeX Configuration with all supported delimiters
 *
 * RENDERING ARCHITECTURE:
 * This component uses a two-stage hybrid approach for complete delimiter support:
 *
 * STAGE 1 - Markdown Processing (remark-math + rehype-katex):
 *   - remark-math: Identifies $...$ and $$...$$ in markdown source
 *   - rehype-katex: Renders these to KaTeX HTML during markdown→HTML conversion
 *   - Advantage: Math content protected from markdown transformations
 *
 * STAGE 2 - DOM Post-Processing (auto-render extension):
 *   - Scans final rendered HTML for remaining delimiters
 *   - Catches \(...\), \[...\], and LaTeX environment delimiters
 *   - Advantage: Supports full LaTeX syntax not handled by remark-math
 *
 * Supported Math Delimiters:
 *
 * INLINE MATH:
 * - $x^2$                    → x² (via remark-math + rehype-katex)
 * - \(x^2\)                  → x² (via auto-render)
 *
 * DISPLAY MATH (centered, block-level):
 * - $$x^2$$                  → Centered equation (via remark-math + rehype-katex)
 * - \[x^2\]                  → Centered equation (via auto-render)
 *
 * LATEX ENVIRONMENTS (via auto-render):
 * - \begin{equation}...\end{equation}           → Numbered equation
 * - \begin{equation*}...\end{equation*}         → Unnumbered equation
 * - \begin{align}...\end{align}                 → Multi-line aligned equations
 * - \begin{align*}...\end{align*}               → Multi-line aligned (no numbers)
 * - \begin{alignat}...\end{alignat}             → Aligned equations with custom spacing
 * - \begin{alignat*}...\end{alignat*}           → Alignat unnumbered
 * - \begin{gather}...\end{gather}               → Multiple centered equations
 * - \begin{gather*}...\end{gather*}             → Gather unnumbered
 * - \begin{CD}...\end{CD}                       → Commutative diagrams
 * - \begin{multline}...\end{multline}           → Multi-line equations
 * - \begin{multline*}...\end{multline*}         → Multline unnumbered
 *
 * NOTES:
 * - $$ is processed before $ to avoid conflicts
 * - Code blocks and pre tags are automatically ignored by auto-render
 * - Elements with class "no-math" are skipped
 * - Errors are logged but don't break rendering (throwOnError: false)
 */
const KATEX_OPTIONS = {
    delimiters: [
        // Display math (processed first to avoid conflicts)
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },

        // Inline math
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },

        // LaTeX environments
        { left: '\\begin{equation}', right: '\\end{equation}', display: true },
        { left: '\\begin{equation*}', right: '\\end{equation*}', display: true },
        { left: '\\begin{align}', right: '\\end{align}', display: true },
        { left: '\\begin{align*}', right: '\\end{align*}', display: true },
        { left: '\\begin{alignat}', right: '\\end{alignat}', display: true },
        { left: '\\begin{alignat*}', right: '\\end{alignat*}', display: true },
        { left: '\\begin{gather}', right: '\\end{gather}', display: true },
        { left: '\\begin{gather*}', right: '\\end{gather*}', display: true },
        { left: '\\begin{CD}', right: '\\end{CD}', display: true },
        { left: '\\begin{multline}', right: '\\end{multline}', display: true },
        { left: '\\begin{multline*}', right: '\\end{multline*}', display: true },
    ],
    // Ignore code blocks and other elements where math shouldn't be rendered
    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option'],
    // Ignore elements with these classes
    ignoredClasses: ['no-math'],
    // Don't throw on errors, just log them
    throwOnError: false,
    // Error callback for debugging
    errorCallback: (msg, err) => {
        console.error('KaTeX rendering error:', msg, err);
    },
    // Preprocess to handle any escaped characters
    preProcess: (text) => {
        // Ensure backslashes are properly preserved
        return text;
    },
};

/**
 * Custom hook to apply KaTeX auto-render to element content
 * Runs after ReactMarkdown has finished rendering
 */
function useKatexAutoRender(contentRef, content) {
    useEffect(() => {
        if (contentRef.current && content) {
            // Use requestAnimationFrame to ensure ReactMarkdown has fully rendered
            const rafId = requestAnimationFrame(() => {
                try {
                    // Apply KaTeX auto-render to catch delimiters not handled by remark-math
                    // This handles \(...\), \[...\], and LaTeX environments
                    renderMathInElement(contentRef.current, KATEX_OPTIONS);
                } catch (error) {
                    console.error('KaTeX auto-render failed:', error);
                }
            });

            return () => cancelAnimationFrame(rafId);
        }
    }, [content]); // Re-run when content changes
}

/**
 * Code Component - handles both inline code and code blocks
 */
function CodeComponent({ children, className, inline, ...props }) {
    // Inline code - simple rendering
    if (inline) {
        return (
            <code className='bg-muted px-1.5 py-0.5 rounded text-[11px] sm:text-xs font-mono break-all' {...props}>
                {children}
            </code>
        );
    }

    // Code block - with syntax highlighting
    return <CodeBlock className={className} {...props}>{children}</CodeBlock>;
}

/**
 * Code Block Component with Shiki highlighting
 */
function CodeBlock({ children, className, ...props }) {
    const [highlightedHtml, setHighlightedHtml] = useState(null);
    const [copied, setCopied] = useState(false);

    // Extract language
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : '';
    const code = String(children).replace(/\n$/, '');

    useEffect(() => {
        if (language) {
            codeToHtml(code, {
                lang: language,
                theme: 'github-dark-default'
            })
                .then((html) => {
                    setHighlightedHtml(html);
                })
                .catch((err) => {
                    console.error('Shiki highlighting error:', err);
                    setHighlightedHtml(null);
                });
        }
    }, [code, language]);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    // Code block with Shiki
    if (highlightedHtml) {
        return (
            <div className="relative my-2 max-w-full">
                <button
                    onClick={handleCopy}
                    className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-all duration-200 z-20"
                    aria-label="Copy code"
                    title={copied ? 'Copied!' : 'Copy code'}
                >
                    {copied ? (
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    ) : (
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                    )}
                </button>
                <div
                    className="overflow-x-auto rounded-md text-xs sm:text-sm max-w-full"
                    dangerouslySetInnerHTML={{ __html: highlightedHtml }}
                />
            </div>
        );
    }

    // Loading or fallback
    return (
        <div className="relative my-2 max-w-full">
            <button
                onClick={handleCopy}
                className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-all duration-200 z-20"
                aria-label="Copy code"
                title={copied ? 'Copied!' : 'Copy code'}
            >
                {copied ? (
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                ) : (
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                )}
            </button>
            <pre className="bg-[#0d1117] text-gray-300 overflow-x-auto rounded-md p-3 text-[11px] sm:text-xs max-w-full">
                <code className="font-mono">{code}</code>
            </pre>
        </div>
    );
}

function MessageBubble({ message, onRetry }) {
    const [mounted, setMounted] = useState(false);
    const isUser    = message.sender === 'user';
    const isError   = message.isError;
    const contentRef = useRef(null);

    // Apply KaTeX auto-render to bot messages
    useKatexAutoRender(contentRef, !isUser ? message.content : null);

    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <div className={cn(
            "flex gap-1.5 sm:gap-3 mb-4 sm:mb-6 animate-in slide-in-from-bottom-2 duration-500 ease-out",
            isUser ? "flex-row-reverse" : "flex-row"
        )}>
            <Avatar className="h-7 w-7 sm:h-8 sm:w-8 mt-1 ring-2 ring-background shadow-sm flex-shrink-0 transition-transform duration-300">
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
                "flex flex-col min-w-0",
                "max-w-[calc(100%-3.5rem)] sm:max-w-[80%] md:max-w-[85%] lg:max-w-[88%]",
                isUser ? "items-end" : "items-start"
            )}>
                <Card className={cn(
                    "shadow-sm border-0 overflow-hidden w-full",
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
                        {isError ? (
                            <div className="space-y-2">
                                <p className='text-xs sm:text-sm whitespace-pre-wrap leading-relaxed m-0 break-words text-destructive'>
                                    {message.content}
                                </p>
                                {onRetry && (
                                    <button
                                        onClick={onRetry}
                                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-destructive bg-destructive/10 hover:bg-destructive/20 rounded-md transition-colors duration-200"
                                    >
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                        </svg>
                                        Try Again
                                    </button>
                                )}
                            </div>
                        ) : isUser ? (
                            <p className='text-xs sm:text-sm whitespace-pre-wrap leading-relaxed m-0 break-words'>{message.content}</p>
                        ) : (
                            <div ref={contentRef} className='text-xs sm:text-sm leading-relaxed prose prose-sm dark:prose-invert [&>p>pre]:!m-0 [&>p:has(pre)]:!p-0' style={{maxWidth: 'none'}}>
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm, remarkMath]}
                                    rehypePlugins={[rehypeKatex]}
                                    unwrapDisallowed={true}
                                    disallowedElements={[]}
                                    components={{
                                        // Regular components - use div for p to avoid nesting issues with code blocks
                                        p: ({node, children, ...props}) => {
                                            // Check if children contain code blocks or code elements
                                            const hasBlockElement = node?.children?.some(
                                                child => child.type === 'element' &&
                                                (child.tagName === 'pre' || child.tagName === 'code')
                                            );
                                            // Use div if there's a block element to avoid invalid HTML nesting
                                            return hasBlockElement ? (
                                                <div className='mb-2 last:mb-0' {...props}>{children}</div>
                                            ) : (
                                                <p className='mb-2 last:mb-0' {...props}>{children}</p>
                                            );
                                        },
                                        ul: ({node, ...props}) => <ul className='mb-2 ml-3 sm:ml-4 list-disc' {...props} />,
                                        ol: ({node, ...props}) => <ol className='mb-2 ml-3 sm:ml-4 list-decimal' {...props} />,
                                        li: ({node, ...props}) => <li className='mb-1 break-words' {...props} />,
                                        pre: ({node, ...props}) => <pre className='my-2' {...props} />,
                                        code: CodeComponent,
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

export default function ChatMessages({ messages, isLoading, agentStatus, thinkingContent, onRetry }) {
    // Check if there's a streaming message
    const hasStreamingMessage = messages.some(msg => msg.isStreaming);

    // Only show typing indicator if loading but no message is streaming yet and not thinking
    const showTypingIndicator = isLoading && !hasStreamingMessage && !agentStatus;

    // Check if agent is thinking
    const isThinking = agentStatus && agentStatus.type === 'thinking';

    return (
        <div className='space-y-1'>
            {messages.map((message) => (
                <MessageBubble key={message.id} message={message} onRetry={message.isError ? onRetry : undefined} />
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