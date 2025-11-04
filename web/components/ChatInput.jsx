'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Paperclip, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/LanguageContext';
import AttachmentPreview from '@/components/AttachmentPreview';

export default function ChatInput({ onSendMessage, disabled }) {
    const { t } = useLanguage();
    const [message, setMessage] = useState('');
    const [isFocused, setIsFocused] = useState(false);
    const [attachments, setAttachments] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef(null);
    const textareaRef = useRef(null);

    // Auto-resize textarea as user types
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            // Reset height to auto to get the correct scrollHeight
            textarea.style.height = 'auto';
            // Set height based on scrollHeight, with max of 200px
            const newHeight = Math.min(textarea.scrollHeight, 200);
            textarea.style.height = `${newHeight}px`;
        }
    }, [message]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if ((message.trim() || attachments.length > 0) && !disabled && !isUploading) {
            onSendMessage(message, attachments);
            setMessage('');
            setAttachments([]);
            // Reset textarea height after sending
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleFileSelect = async (e) => {
        const files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        setIsUploading(true);

        try {
            const uploadPromises = files.map(async (file) => {
                // Validate file type
                const allowedTypes = [
                    'image/jpeg',
                    'image/jpg',
                    'image/png',
                    'image/webp',
                    'application/pdf',
                    'text/csv',
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ];
                if (!allowedTypes.includes(file.type)) {
                    throw new Error(`Invalid file type: ${file.type}. Only images, PDFs, CSV, and Excel files are allowed.`);
                }

                // Create preview for images
                let preview = null;
                if (file.type.startsWith('image/')) {
                    preview = URL.createObjectURL(file);
                }

                // Upload file to server using v2 endpoint
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/v2/upload/file', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.message || 'Upload failed');
                }

                const result = await response.json();

                return {
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    path: result.data.path,
                    preview,
                };
            });

            const uploadedFiles = await Promise.all(uploadPromises);
            setAttachments(prev => [...prev, ...uploadedFiles]);

        } catch (error) {
            console.error('File upload error:', error);
            alert(error.message || 'Failed to upload file. Please try again.');
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleRemoveAttachment = (index) => {
        setAttachments(prev => {
            const newAttachments = [...prev];
            // Revoke preview URL if it exists
            if (newAttachments[index].preview) {
                URL.revokeObjectURL(newAttachments[index].preview);
            }
            newAttachments.splice(index, 1);
            return newAttachments;
        });
    };

    const handleAttachClick = () => {
        fileInputRef.current?.click();
    };

    const handleKeyDown = (e) => {
        // Submit on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
        // Allow Shift+Enter for new lines
    };

    const hasMessage = message.trim().length > 0;
    const canSubmit = (hasMessage || attachments.length > 0) && !disabled && !isUploading;

    return (
        <div className="p-3 sm:p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            {/* Hidden file input */}
            <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp,application/pdf,text/csv,.csv,application/vnd.ms-excel,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,.xlsx"
                multiple
                onChange={handleFileSelect}
                className="hidden"
            />

            {/* Attachments Preview */}
            {attachments.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-2">
                    {attachments.map((file, index) => (
                        <AttachmentPreview
                            key={index}
                            file={file}
                            onRemove={() => handleRemoveAttachment(index)}
                        />
                    ))}
                </div>
            )}

            <form onSubmit={handleSubmit} className="flex items-end gap-3">
                <div className="flex-1 relative group">
                    <div className={cn(
                        "relative rounded-xl border transition-all duration-300 ease-in-out",
                        "bg-background/50 backdrop-blur-sm",
                        isFocused
                            ? "border-primary/50 shadow-lg shadow-primary/10 ring-2 ring-primary/20"
                            : "border-border hover:border-border/80",
                        disabled && "opacity-50"
                    )}>
                        <Textarea
                            ref={textareaRef}
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                            placeholder={t('chat.placeholder')}
                            disabled={disabled}
                            rows={1}
                            className={cn(
                                "border-0 bg-transparent pr-16 pl-4 py-3 min-h-[52px] max-h-[200px]",
                                "text-base placeholder:text-muted-foreground/70",
                                "focus-visible:ring-0 focus-visible:ring-offset-0",
                                "resize-none transition-all duration-200",
                                "overflow-y-auto scrollbar-thin"
                            )}
                        />

                        <div className="absolute right-2 top-3 flex items-center gap-1">
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={handleAttachClick}
                                className={cn(
                                    "h-8 w-8 p-0 rounded-lg transition-all duration-200",
                                    "hover:bg-muted/80 hover:scale-105 active:scale-95",
                                    isUploading
                                        ? "text-primary"
                                        : attachments.length > 0
                                            ? "text-primary"
                                            : "text-muted-foreground hover:text-foreground"
                                )}
                                disabled={disabled || isUploading}
                            >
                                {isUploading ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Paperclip className="h-4 w-4" />
                                )}
                            </Button>

                        </div>
                    </div>
                </div>

                <Button
                    type="submit"
                    disabled={!canSubmit}
                    className={cn(
                        "h-[52px] w-[52px] p-0 rounded-xl transition-all duration-300 ease-in-out flex-shrink-0",
                        "relative overflow-hidden group self-end",
                        canSubmit
                            ? [
                                "bg-primary hover:bg-primary/90 shadow-lg shadow-primary/25",
                                "hover:shadow-xl hover:shadow-primary/30 hover:scale-105",
                                "active:scale-95 active:shadow-md"
                            ]
                            : [
                                "bg-muted/50 text-muted-foreground cursor-not-allowed",
                                "hover:bg-muted/50 hover:scale-100 shadow-none"
                            ]
                    )}
                >
                    <div className={cn(
                        "transition-all duration-200",
                        canSubmit
                            ? "group-hover:rotate-12 group-active:rotate-0"
                            : ""
                    )}>
                        <Send className="h-5 w-5" />
                    </div>

                    {canSubmit && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/10 to-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    )}
                </Button>
            </form>

            {message.length > 0 && (
                <div className="flex justify-between items-center mt-2 px-1">
                    <div className="text-xs text-muted-foreground/60">
                        {message.length > 500 && (
                            <span className={message.length > 1000 ? "text-destructive" : "text-warning"}>
                                {message.length}/1000
                            </span>
                        )}
                    </div>
                    <div className="text-xs text-muted-foreground/60">
                        {t('chat.keyboardShortcut')}
                    </div>
                </div>
            )}
        </div>
    );
}
