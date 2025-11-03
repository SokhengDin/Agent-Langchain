import { NextResponse } from "next/server";

const LLM_API_BASE_URL = process.env.NEXT_PUBLIC_LLM_API_BASE_URL || 'http://localhost:8005';

export async function POST(request) {
    try {
        const body = await request.json();

        // Proxy the request to the DS Agent backend
        const response = await fetch(`${LLM_API_BASE_URL}/api/v2/ds-agent/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: 'Failed to communicate with DS Agent'
            }));
            return NextResponse.json(error, { status: response.status });
        }

        const result = await response.json();
        return NextResponse.json(result);

    } catch (error) {
        console.error('DS Agent chat proxy error:', error);
        return NextResponse.json(
            {
                detail: `Error processing chat request: ${error.message}`
            },
            { status: 500 }
        );
    }
}
