import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

export async function POST(request: NextRequest) {
    try {
        // 1. Extract the file payload incoming from the browser
        const formData = await request.formData();

        // 2. Safely read keys from container runtime variables
        const backendUrl = process.env.BACKEND_URL || "http://enterprise-rag-backend:8000";
        const apiKey = process.env.BACKEND_API_KEY || "";

        // 3. Forward the request to your FastAPI container internally with authentication
        const response = await axios.post(`${backendUrl}/upload`, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
                "X-API-Key": apiKey // 🔥 Injects your secret key here securely
            },
        });

        // 4. Send the successful response back to the client UI
        return NextResponse.json(response.data);
    } catch (error: any) {
        console.error("API Gateway Proxy Error:", error.message);
        return NextResponse.json(
            { error: "Secure proxy upload pipeline failed." },
            { status: 500 }
        );
    }
}