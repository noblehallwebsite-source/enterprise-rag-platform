// ~/enterprise-rag-platform/frontend/src/app/api/upload/route.ts
import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

export async function POST(request: NextRequest) {
    try {
        // 1. Extract the file payload incoming from the user's browser
        const formData = await request.formData();

        // 2. Read the private variable from our secure container environment
        const backendUrl = process.env.BACKEND_URL || "http://enterprise-rag-backend:8000";

        // 3. Forward the request to your FastAPI backend internally
        const response = await axios.post(`${backendUrl}/upload`, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        // 4. Return the backend's response (including taskId) back to the browser
        return NextResponse.json(response.data);
    } catch (error: any) {
        console.error("API Gateway Proxy Error:", error.message);
        return NextResponse.json(
            { error: "Secure proxy upload pipeline failed." },
            { status: 500 }
        );
    }
}