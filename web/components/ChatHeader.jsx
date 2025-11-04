'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Bot, Circle, BrainCircuit, Hotel } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import LanguageToggle from './LanguageToggle';

export default function ChatHeader({ activeAgent = 'ds-agent' }) {
    const { t } = useLanguage();

    const agentConfig = {
        'ds-agent': {
            title: t('chat.dsTitle'),
            badge: 'DS Agent',
            icon: BrainCircuit,
            color: 'bg-purple-500'
        },
        'hotel-agent': {
            title: t('chat.title'),
            badge: 'Hotel Agent',
            icon: Hotel,
            color: 'bg-primary'
        }
    };

    const config = agentConfig[activeAgent];
    const AgentIcon = config.icon;

    return (
        <div className='p-3 sm:p-4'>
            <div className='flex items-center justify-between'>
                <div className='flex items-center space-x-2 sm:space-x-3'>
                    <Avatar className='h-8 w-8 sm:h-10 sm:w-10'>
                        <AvatarImage src="/agent-avater.png" alt="AI Agent" />
                        <AvatarFallback className={`${config.color} text-primary-foreground`}>
                            <AgentIcon className='h-4 w-4 sm:h-5 sm:w-5' />
                        </AvatarFallback>
                    </Avatar>
                    <div>
                        <div className='flex items-center gap-2'>
                            <h3 className='font-semibold text-sm sm:text-lg'>{config.title}</h3>
                            <span className='text-[9px] sm:text-[10px] text-muted-foreground/60 hidden sm:inline'>
                                • {t('footer.developedBy')}
                            </span>
                        </div>
                        <div className='flex items-center space-x-2'>
                            <Circle className='h-2 w-2 fill-green-500 text-green-500' />
                            <span className='text-xs sm:text-sm text-muted-foreground'>Online</span>
                        </div>
                    </div>
                    <Badge variant="secondary" className="text-xs font-medium hidden sm:inline-flex">
                        {config.badge}
                    </Badge>
                </div>

                <div className="flex items-center">
                    <LanguageToggle />
                </div>
            </div>
        </div>
    )
}