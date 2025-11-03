import { NextResponse } from 'next/server';

const LLM_API_BASE_URL = process.env.NEXT_PUBLIC_LLM_API_BASE_URL || 'http://localhost:8005';

export async function POST(request) {
    try {
        const formData = await request.formData();

        // Forward the entire FormData to the LLM backend
        const response = await fetch(`${LLM_API_BASE_URL}/api/v2/upload/file`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            return NextResponse.json(error, { status: response.status });
        }

        const result = await response.json();
        return NextResponse.json(result);

    } catch (error) {
        console.error('File upload proxy error:', error);
        return NextResponse.json(
            {
                status: 'error',
                message: 'Failed to upload file',
                error: 'UPLOAD_FAILED',
                details: error.message
            },
            { status: 500 }
        );
    }
}

// GET endpoint to check upload configuration
export async function GET() {
    try {
        const response = await fetch(`${LLM_API_BASE_URL}/api/v2/upload/file`, {
            method: 'GET',
        });

        if (!response.ok) {
            throw new Error('Failed to fetch upload configuration');
        }

        const result = await response.json();
        return NextResponse.json(result);

    } catch (error) {
        return NextResponse.json({
            status: 'success',
            data: {
                maxFileSizeMB: 10,
                allowedTypes: [
                    'image/jpeg',
                    'image/jpg',
                    'image/png',
                    'image/webp',
                    'application/pdf',
                    'text/csv',
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ],
                categories: ['images', 'documents', 'spreadsheets'],
                endpoints: {
                    image: '/api/v2/upload/image',
                    pdf: '/api/v2/upload/pdf',
                    file: '/api/v2/upload/file'
                }
            }
        });
    }
}
