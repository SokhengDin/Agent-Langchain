import { NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function GET(request, { params }) {
    try {
        const { booking_id } = await params;

        // Proxy the request to the backend
        const response = await fetch(`${API_BASE_URL}/api/v1/invoice/${booking_id}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/pdf',
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                message: 'Failed to generate invoice'
            }));
            return NextResponse.json(error, { status: response.status });
        }

        // Get the PDF content as a buffer
        const pdfBuffer = await response.arrayBuffer();

        // Return the PDF with appropriate headers
        return new NextResponse(pdfBuffer, {
            status: 200,
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `inline; filename=invoice_${booking_id}.pdf`,
            },
        });

    } catch (error) {
        console.error('Invoice generation proxy error:', error);
        return NextResponse.json(
            {
                status: 'error',
                message: 'Failed to generate invoice',
                error: 'INVOICE_GENERATION_FAILED',
                details: error.message
            },
            { status: 500 }
        );
    }
}
