'use client';

import { X, FileText, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export default function AttachmentPreview({ file, onRemove }) {
    const isImage = file.type?.startsWith('image/');
    const isPDF = file.type === 'application/pdf';

    return (
        <div className={cn(
            "relative group rounded-lg border border-border/50 p-2",
            "bg-muted/30 hover:bg-muted/50 transition-colors duration-200",
            "flex items-center gap-3"
        )}>
            {/* File Icon/Preview */}
            <div className={cn(
                "flex-shrink-0 w-12 h-12 rounded-md overflow-hidden",
                "bg-background border border-border/50",
                "flex items-center justify-center"
            )}>
                {isImage && file.preview ? (
                    <img
                        src={file.preview}
                        alt={file.name}
                        className="w-full h-full object-cover"
                    />
                ) : isPDF ? (
                    <FileText className="w-6 h-6 text-destructive" />
                ) : (
                    <ImageIcon className="w-6 h-6 text-primary" />
                )}
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate text-foreground">
                    {file.name}
                </p>
                <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(1)} KB
                </p>
            </div>

            {/* Remove Button */}
            <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onRemove}
                className={cn(
                    "h-6 w-6 p-0 rounded-full",
                    "opacity-0 group-hover:opacity-100 transition-opacity",
                    "hover:bg-destructive hover:text-destructive-foreground"
                )}
            >
                <X className="h-3 w-3" />
            </Button>
        </div>
    );
}
