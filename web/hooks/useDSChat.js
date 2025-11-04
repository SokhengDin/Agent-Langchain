'use client';

import { useState, useEffect } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import { logAndGetUserMessage, ApiError } from "@/lib/apiErrorHandler";

export function useDSChat() {
    const { t } = useLanguage();

    const [messages, setMessages] = useState([
        {
            id: 1,
            content: t('chat.dsGreeting'),
            sender: 'agent',
            timestamp: new Date().toISOString(),
        }
    ]);

    const [isLoading, setIsLoading] = useState(false);
    const [threadId, setThreadId] = useState(null);
    const [agentStatus, setAgentStatus] = useState(null);
    const [thinkingContent, setThinkingContent] = useState('');

    // Update the initial greeting message when language changes
    useEffect(() => {
        setMessages(prev => {
            const updatedMessages = [...prev];
            if (updatedMessages.length > 0 && updatedMessages[0].id === 1 && updatedMessages[0].sender === 'agent') {
                updatedMessages[0] = {
                    ...updatedMessages[0],
                    content: t('chat.dsGreeting')
                };
            }
            return updatedMessages;
        });
    }, [t]);

    const sendMessage = async (content, attachments = []) => {
        const userMessage = {
            id: Date.now(),
            content: content,
            sender: 'user',
            timestamp: new Date().toISOString(),
            attachments: attachments.length > 0 ? attachments : undefined,
        };
        setMessages(prev => [...prev, userMessage]);

        setIsLoading(true);

        const agentMessageId = Date.now() + 1;
        let messageCreated = false;

        try {
            // Prepare request body
            const requestBody = {
                message: content,
                thread_id: threadId,
            };

            // Add uploaded files array if attachments exist
            if (attachments.length > 0) {
                requestBody.uploaded_files = attachments.map(att => att.path);
            }

            const response = await fetch('/api/v2/ds-agent/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                throw new ApiError(`Request failed with status ${response.status}`, response.status, null);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');

                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event = JSON.parse(line.slice(6));

                            switch (event.type) {
                                case 'start':
                                    if (event.thread_id) {
                                        setThreadId(event.thread_id);
                                        console.log('DS Agent started with thread_id:', event.thread_id);
                                    }
                                    break;

                                case 'token':
                                    setAgentStatus(null);
                                    setThinkingContent('');

                                    if (!messageCreated) {
                                        messageCreated = true;
                                        const agentMessage = {
                                            id: agentMessageId,
                                            content: event.content,
                                            sender: 'agent',
                                            timestamp: new Date().toISOString(),
                                            isStreaming: true,
                                        };
                                        setMessages(prev => [...prev, agentMessage]);
                                    } else {
                                        setMessages(prev => prev.map(msg =>
                                            msg.id === agentMessageId
                                                ? { ...msg, content: msg.content + event.content }
                                                : msg
                                        ));
                                    }
                                    break;

                                case 'thinking':
                                    if (event.content) {
                                        setThinkingContent(prev => prev + event.content);
                                    }
                                    setAgentStatus({
                                        type: 'thinking',
                                        content: event.content || '',
                                        reasoningTokens: event.reasoning_tokens
                                    });
                                    break;

                                case 'tool_call':
                                    console.log('DS Agent tool called:', event.tool_calls);
                                    setAgentStatus({
                                        type: 'tool_call',
                                        toolCalls: event.tool_calls
                                    });
                                    break;

                                case 'thinking_stats':
                                    console.log('Reasoning tokens used:', event.reasoning_tokens);
                                    break;

                                case 'done':
                                    console.log('DS Agent stream complete');
                                    setAgentStatus(null);
                                    setThinkingContent('');
                                    if (event.thread_id) {
                                        setThreadId(event.thread_id);
                                        console.log('Updated DS Agent threadId to:', event.thread_id);
                                    }
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === agentMessageId
                                            ? { ...msg, isStreaming: false }
                                            : msg
                                    ));
                                    break;

                                case 'error':
                                    throw new ApiError(event.error, 500, null);
                            }
                        } catch (parseError) {
                            console.error('Failed to parse DS Agent SSE event:', parseError);
                        }
                    }
                }
            }

        } catch (error) {
            setAgentStatus(null);
            setThinkingContent('');
            setMessages(prev => prev.filter(msg => msg.id !== agentMessageId));

            const userErrorMessage = logAndGetUserMessage(error, 'DS Agent Chat');

            const errorMessage = {
                id: Date.now() + 1,
                content: userErrorMessage,
                sender: 'agent',
                timestamp: new Date().toISOString(),
                isError: true,
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        isLoading,
        sendMessage,
        threadId,
        agentStatus,
        thinkingContent
    };
}
