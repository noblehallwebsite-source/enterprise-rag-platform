// frontend/src/services/documents.ts
import { Document } from "@/types/document";

export async function getDocuments(): Promise<Document[]> {
    // Nginx routes relative /api requests back directly to FastAPI port 8000
    const response = await fetch("/api/documents?tenant_id=company-a", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": "dev-key-company-a", // Explicitly passing your gateway token
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch documents: ${response.statusText}`);
    }

    return response.json();
}