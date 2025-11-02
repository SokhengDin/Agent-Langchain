'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Bot, Circle } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import LanguageToggle from './LanguageToggle';

export default function ChatHeader() {
    const { t } = useLanguage();

    return (
        <div className='p-4 border-b'>
            <div className='flex items-center justify-between'>
                <div className='flex items-center space-x-3'>
                    <Avatar className='h-10 w-10'>
                        <AvatarImage src="/agent-avater.png" alt="AI Agent" />
                        <AvatarFallback className="bg-primary text-primary-foreground" >
                            <Bot className='h-5 w-5' />
                        </AvatarFallback>
                    </Avatar>
                    <div>
                        <h3 className='font-semibold text-lg'>{t('chat.title')}</h3>
                        <div className='flex items-center space-x-2'>
                            <Circle className='h-2 w-2 fill-green-500 text-green-500' />
                            <span className='text-sm text-muted-foreground'>Online</span>
                        </div>
                    </div>
                    <Badge variant="secondary" className="text-xs font-medium">
                        Agent Chat
                    </Badge>
                </div>
                
                <div className="flex items-center">
                    <LanguageToggle />
                </div>
            </div>
        </div>
    )
}