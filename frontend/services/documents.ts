// frontend/src/services/documents.ts
import { Document, DocumentDetailsPayload } from "@/types/document";

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


// frontend/src/services/documents.ts

export async function deleteDocument(documentId: string): Promise<{ message: string }> {
    const response = await fetch(`/api/documents/${documentId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": "dev-key-company-a",
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to delete document: ${response.statusText}`);
    }

    return response.json();
}



/**
 * Fetches relational system metrics combined with raw vector chunk arrays 
 * from the backend document observability endpoint.
 */
export async function getDocumentDetails(documentId: string): Promise<DocumentDetailsPayload> {
    const response = await fetch(`/api/documents/${documentId}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": "dev-key-company-a", // Bypasses Nginx proxy gateway credentials check
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch observability details: ${response.statusText}`);
    }

    return response.json();
}


