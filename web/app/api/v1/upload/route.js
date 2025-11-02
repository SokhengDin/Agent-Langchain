import { NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

const UPLOAD_DIR = path.join(process.cwd(), 'uploads');
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Allowed file types
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
const ALLOWED_PDF_TYPES = ['application/pdf'];
const ALLOWED_TYPES = [...ALLOWED_IMAGE_TYPES, ...ALLOWED_PDF_TYPES];

// Get file extension from mime type
const getExtension = (mimeType) => {
    const extensions = {
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'image/png': 'png',
        'image/webp': 'webp',
        'application/pdf': 'pdf'
    };
    return extensions[mimeType] || 'bin';
};

// Determine file category
const getFileCategory = (mimeType) => {
    if (ALLOWED_IMAGE_TYPES.includes(mimeType)) {
        return 'images';
    } else if (ALLOWED_PDF_TYPES.includes(mimeType)) {
        return 'documents';
    }
    return 'others';
};

export async function POST(request) {
    try {
        const formData = await request.formData();
        const file = formData.get('file');

        if (!file) {
            return NextResponse.json(
                { error: 'No file uploaded' },
                { status: 400 }
            );
        }

        // Validate file type
        if (!ALLOWED_TYPES.includes(file.type)) {
            return NextResponse.json(
                {
                    error: 'Invalid file type. Only images (JPEG, PNG, WebP) and PDFs are allowed.',
                    allowedTypes: ALLOWED_TYPES
                },
                { status: 400 }
            );
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            return NextResponse.json(
                { error: `File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB` },
                { status: 400 }
            );
        }

        // Create upload directory if it doesn't exist
        const category = getFileCategory(file.type);
        const categoryDir = path.join(UPLOAD_DIR, category);

        if (!existsSync(UPLOAD_DIR)) {
            await mkdir(UPLOAD_DIR, { recursive: true });
        }
        if (!existsSync(categoryDir)) {
            await mkdir(categoryDir, { recursive: true });
        }

        // Generate unique filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
        const uniqueId = uuidv4().split('-')[0];
        const extension = getExtension(file.type);
        const filename = `${timestamp}_${uniqueId}.${extension}`;
        const filepath = path.join(categoryDir, filename);

        // Convert file to buffer and save
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);
        await writeFile(filepath, buffer);

        // Return the relative path from project root
        const relativePath = `/uploads/${category}/${filename}`;

        return NextResponse.json({
            success: true,
            file: {
                name: file.name,
                type: file.type,
                size: file.size,
                path: relativePath,
                category: category,
                uploadedAt: new Date().toISOString()
            }
        });

    } catch (error) {
        console.error('Upload error:', error);
        return NextResponse.json(
            { error: 'Failed to upload file', details: error.message },
            { status: 500 }
        );
    }
}

// GET endpoint to check upload directory status
export async function GET() {
    return NextResponse.json({
        uploadDir: UPLOAD_DIR,
        maxFileSize: MAX_FILE_SIZE,
        allowedTypes: ALLOWED_TYPES,
        categories: ['images', 'documents']
    });
}
