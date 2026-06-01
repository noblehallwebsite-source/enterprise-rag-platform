// frontend/src/types/document.ts
export interface Document {
    id: string;
    tenant_id: string;
    filename: string;
    status: "PROCESSING" | "COMPLETED" | "FAILED" | string;
    chunks_created: number;
    created_at: string;
}