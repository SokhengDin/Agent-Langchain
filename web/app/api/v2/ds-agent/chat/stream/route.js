import { NextResponse } from "next/server";

const LLM_API_BASE_URL = process.env.NEXT_PUBLIC_LLM_API_BASE_URL || 'http://localhost:8005';

export async function POST(request) {
    try {
        const body = await request.json();

        // Proxy the streaming request to the DS Agent backend
        const response = await fetch(`${LLM_API_BASE_URL}/api/v2/ds-agent/chat/stream`, {
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

        // Stream the response back to the client
        const stream = new ReadableStream({
            async start(controller) {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                try {
                    while (true) {
                        const { done, value } = await reader.read();

                        if (done) {
                            controller.close();
                            break;
                        }

                        // Forward the chunk as-is
                        controller.enqueue(value);
                    }
                } catch (error) {
                    console.error('Stream error:', error);
                    controller.error(error);
                }
            }
        });

        return new NextResponse(stream, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        });

    } catch (error) {
        console.error('DS Agent stream proxy error:', error);
        return NextResponse.json(
            {
                detail: `Error processing stream request: ${error.message}`
            },
            { status: 500 }
        );
    }
}
