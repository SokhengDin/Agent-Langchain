import { NextResponse } from 'next/server';

const LLM_API_BASE_URL = process.env.NEXT_PUBLIC_LLM_API_BASE_URL || 'http://localhost:8005';

export async function POST(request) {
    try {
        const formData = await request.formData();

        // Forward the entire FormData to the LLM backend
        const response = await fetch(`${LLM_API_BASE_URL}/api/v2/upload/pdf`, {
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
        console.error('PDF upload proxy error:', error);
        return NextResponse.json(
            {
                status: 'error',
                message: 'Failed to upload PDF',
                error: 'UPLOAD_FAILED',
                details: error.message
            },
            { status: 500 }
        );
    }
}
