import { llmApi } from "@/lib/api";

export async function POST(request) {
    try {
        const body = await request.json();
        const authHeader = request.headers.get("authorization");

        if (!authHeader) {
            return new Response(
                JSON.stringify({
                    status: 401,
                    message: "No authorization token provided",
                    data: null
                }),
                {
                    status: 401,
                    headers: { 'Content-Type': 'application/json' }
                }
            );
        }

        // Create a ReadableStream for Server-Sent Events
        const stream = new ReadableStream({
            async start(controller) {
                try {
                    const response = await llmApi.post(
                        "/api/v2/hotel-agent/chat/stream",
                        body,
                        {
                            headers: {
                                Authorization: authHeader,
                            },
                            responseType: 'stream'
                        }
                    );

                    // Handle the streaming response
                    response.data.on('data', (chunk) => {
                        controller.enqueue(chunk);
                    });

                    response.data.on('end', () => {
                        controller.close();
                    });

                    response.data.on('error', (error) => {
                        console.error('Stream error:', error);
                        const errorEvent = `data: ${JSON.stringify({
                            type: 'error',
                            error: error.message || 'Stream error occurred'
                        })}\n\n`;
                        controller.enqueue(new TextEncoder().encode(errorEvent));
                        controller.close();
                    });

                } catch (error) {
                    console.error("Stream initialization error:", error);
                    const errorEvent = `data: ${JSON.stringify({
                        type: 'error',
                        error: error.response?.data?.message || error.message || 'Failed to initialize stream'
                    })}\n\n`;
                    controller.enqueue(new TextEncoder().encode(errorEvent));
                    controller.close();
                }
            }
        });

        return new Response(stream, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        });

    } catch (error) {
        console.error("Chat stream error:", error);
        return new Response(
            JSON.stringify({
                status: 500,
                message: "Internal server error",
                data: null
            }),
            {
                status: 500,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}
