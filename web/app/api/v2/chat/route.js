import { NextResponse } from "next/server";
import { llmApi } from "@/lib/api";

export async function POST(request) {
    try {
        const body = await request.json();

        const authHeader = request.headers.get("authorization");

        if (!authHeader) {
            return NextResponse.json(
                {
                    status: 401,
                    message: "No authorization token provided",
                    data: null
                },
                { status: 401 }
            );
        }
        const result = await llmApi.post(
            "/api/v2/hotel-agent/chat",
            body,
            {
                headers: {
                    Authorization: authHeader,
                },
            }
        );

        console.log('Chat response:', result.data);

        return NextResponse.json(result.data, { status: 200 });
    } catch (error) {
        console.error("Chat error:", error);
        console.error("Error details:", {
            message: error.message,
            response: error.response?.data,
            status: error.response?.status
        });

        if (error.response) {
            return NextResponse.json(
                error.response.data || {
                    status: error.response.status,
                    message: error.response.data?.message || "Chat request failed",
                    data: null
                },
                { status: error.response.status }
            );
        }

        return NextResponse.json(
            {
                status: 500,
                message: "Internal server error",
                data: null
            },
            { status: 500 }
        );
    }
}