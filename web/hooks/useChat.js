'use client';

import { useState, useEffect } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { authHelpers } from "@/lib/auth";
import { logAndGetUserMessage, ApiError } from "@/lib/apiErrorHandler";

export function useChat() {
    const { t } = useLanguage();
    const { handleAuthError } = useAuth();
    const [messages, setMessages] = useState([
        {
            id: 1,
            content: t('chat.greeting'),
            sender: 'agent',
            timestamp: new Date().toISOString(),
        }
    ]);

    const [isLoading, setIsLoading] = useState(false);
    const [threadId, setThreadId]   = useState(null);
    const [agentStatus, setAgentStatus] = useState(null); // For showing tool calls and thinking
    const [thinkingContent, setThinkingContent] = useState(''); // For accumulating thinking tokens

    // Update the initial greeting message when language changes
    useEffect(() => {
        setMessages(prev => {
            const updatedMessages = [...prev];
            if (updatedMessages.length > 0 && updatedMessages[0].id === 1 && updatedMessages[0].sender === 'agent') {
                updatedMessages[0] = {
                    ...updatedMessages[0],
                    content: t('chat.greeting')
                };
            }
            return updatedMessages;
        });
    }, [t]);

    const sendMessage = async (content) => {
        const userMessage = {
            id: Date.now(),
            content,
            sender: 'user',
            timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, userMessage]);

        setIsLoading(true);

        // We'll add the message once we receive the first token
        const agentMessageId = Date.now() + 1;
        let messageCreated = false;

        try {
            const token = authHelpers.getToken();

            if (!token) {
                handleAuthError();
                throw new ApiError('Please login to continue chatting.', 401, null);
            }

            const response = await fetch('/api/v2/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    message: content,
                    thread_id: threadId,
                }),
            });

            if (!response.ok) {
                if (response.status === 401) {
                    handleAuthError();
                    throw new ApiError('Your session has expired. Please login again.', 401, null);
                }
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

                // Keep the last incomplete line in the buffer
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event = JSON.parse(line.slice(6));

                            switch (event.type) {
                                case 'start':
                                    if (event.thread_id) {
                                        setThreadId(event.thread_id);
                                        console.log('Started stream with thread_id:', event.thread_id);
                                    }
                                    break;

                                case 'token':
                                    // Clear agent status and thinking content when tokens start arriving
                                    setAgentStatus(null);
                                    setThinkingContent('');

                                    // Create message on first token, then append subsequent tokens
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
                                        // Append token to the streaming message
                                        setMessages(prev => prev.map(msg =>
                                            msg.id === agentMessageId
                                                ? { ...msg, content: msg.content + event.content }
                                                : msg
                                        ));
                                    }
                                    break;

                                case 'thinking':
                                    // Accumulate thinking tokens
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
                                    console.log('Tool called:', event.tool_calls);
                                    setAgentStatus({
                                        type: 'tool_call',
                                        toolCalls: event.tool_calls
                                    });
                                    break;

                                case 'step_complete':
                                    console.log('Step complete:', event.step);
                                    break;

                                case 'done':
                                    console.log('Stream complete');
                                    setAgentStatus(null);
                                    setThinkingContent('');
                                    if (event.thread_id) {
                                        setThreadId(event.thread_id);
                                        console.log('Updated threadId to:', event.thread_id);
                                    }
                                    // Mark message as no longer streaming
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
                            console.error('Failed to parse SSE event:', parseError);
                        }
                    }
                }
            }

        } catch (error) {
            // Clear agent status and thinking content
            setAgentStatus(null);
            setThinkingContent('');

            // Remove the streaming message and show error
            setMessages(prev => prev.filter(msg => msg.id !== agentMessageId));

            // Handle 401 errors
            if (error instanceof ApiError && error.status === 401) {
                handleAuthError();
            }

            // Log error and get user-friendly message
            const userErrorMessage = logAndGetUserMessage(error, 'Chat');

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