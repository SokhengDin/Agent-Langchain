'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Paperclip, Smile } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/LanguageContext';

export default function ChatInput({ onSendMessage, disabled }) {
    const { t } = useLanguage();
    const [message, setMessage] = useState('');
    const [isFocused, setIsFocused] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !disabled) {
            onSendMessage(message);
            setMessage('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const hasMessage = message.trim().length > 0;

    return (
        <div className="p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
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
                        <Input  
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                            placeholder={t('chat.placeholder')}
                            disabled={disabled}
                            className={cn(
                                "border-0 bg-transparent pr-16 pl-4 py-3 min-h-[52px]",
                                "text-base placeholder:text-muted-foreground/70",
                                "focus-visible:ring-0 focus-visible:ring-offset-0",
                                "resize-none transition-all duration-200"
                            )}
                        />
                        
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                className={cn(
                                    "h-8 w-8 p-0 rounded-lg transition-all duration-200",
                                    "hover:bg-muted/80 hover:scale-105 active:scale-95",
                                    "text-muted-foreground hover:text-foreground"
                                )}
                                disabled={disabled}
                            >
                                <Paperclip className="h-4 w-4" />
                            </Button>
                        
                        </div>
                    </div>
                </div>
                
                <Button
                    type="submit"
                    disabled={disabled || !hasMessage}
                    className={cn(
                        "h-[52px] w-[52px] p-0 rounded-xl transition-all duration-300 ease-in-out",
                        "relative overflow-hidden group",
                        hasMessage && !disabled
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
                        hasMessage && !disabled 
                            ? "group-hover:rotate-12 group-active:rotate-0" 
                            : ""
                    )}>
                        <Send className="h-5 w-5" />
                    </div>
                    
                    {hasMessage && !disabled && (
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