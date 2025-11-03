import { NextResponse } from "next/server";

const LLM_API_BASE_URL = process.env.NEXT_PUBLIC_LLM_API_BASE_URL || 'http://localhost:8005';

export async function GET(request, { params }) {
    try {
        // Get the file path from the params
        const filePath = params.path.join('/');

        // Proxy the request to the backend
        const response = await fetch(`${LLM_API_BASE_URL}/api/v2/files/${filePath}`, {
            method: 'GET',
            headers: {
                'Accept': '*/*',
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: 'File not found'
            }));
            return NextResponse.json(error, { status: response.status });
        }

        // Get the content type from the backend response
        const contentType = response.headers.get('content-type') || 'application/octet-stream';

        // Get the file content as a buffer
        const fileBuffer = await response.arrayBuffer();

        // Determine filename from path
        const filename = filePath.split('/').pop();

        // Return the file with appropriate headers
        return new NextResponse(fileBuffer, {
            status: 200,
            headers: {
                'Content-Type': contentType,
                'Content-Disposition': `inline; filename="${filename}"`,
                'Cache-Control': 'public, max-age=3600', // Cache for 1 hour
            },
        });

    } catch (error) {
        console.error('File serving proxy error:', error);
        return NextResponse.json(
            {
                detail: `Error serving file: ${error.message}`
            },
            { status: 500 }
        );
    }
}
