import { NextResponse } from "next/server";
import { api } from "@/lib/api";

export async function POST(request) {
    try {
        const authHeader = request.headers.get("authorization");

        if (!authHeader) {
            return NextResponse.json(
                { error: "No authorization token provided" },
                { status: 401 }
            );
        }

        const result = await api.post(
            "/api/v1/auth/logout",
            {},
            {
                headers: {
                    Authorization: authHeader,
                },
            }
        );

        return NextResponse.json(result.data, { status: 200 });
    } catch (error) {
        console.error("Logout error:", error);

        if (error.response) {
            return NextResponse.json(
                { error: error.response.data?.message || "Logout failed" },
                { status: error.response.status }
            );
        }

        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        );
    }
}