// frontend/src/services/chat.ts

export interface ChatSessionPayload {
    id: string;
    title: string;
    created_at: string;
}

export interface HistoricalMessagesPayload {
    session_id: string;
    messages: Array<{
        role: "user" | "assistant";
        content: string;
        created_at: string;
    }>;
}

const SECURITY_HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "dev-key-company-a", // Bypasses gateway proxy credential checks
};

/**
 * Tells PostgreSQL to allocate a brand new multi-tenant session thread tracker row.
 */
export async function createChatSession(title: string): Promise<ChatSessionPayload> {
    const response = await fetch("/api/chat/sessions", {
        method: "POST",
        headers: SECURITY_HEADERS,
        body: JSON.stringify({ title }),
    });

    if (!response.ok) {
        // Capture validation errors, CORS errors, or routing failures directly from FastAPI
        const textError = await response.text();
        console.error(`🔴 [Chat Session Failure] Status: ${response.status} | Payload:`, textError);
        throw new Error(`Failed to spin up backend chat thread record. Status: ${response.status}`);
    }
    return response.json();
}

/**
 * Pulls all available conversation summaries registered under the active tenant context.
 */
export async function fetchAllSessions(): Promise<ChatSessionPayload[]> {
    const response = await fetch("/api/chat/sessions", {
        method: "GET",
        headers: SECURITY_HEADERS,
    });
    if (!response.ok) throw new Error("Failed to sync historical sessions ledger.");
    return response.json();
}

/**
 * Returns the exact historical message timeline array for a verified active session thread.
 */
export async function fetchSessionHistory(sessionId: string): Promise<HistoricalMessagesPayload> {
    const response = await fetch(`/api/chat/sessions/${sessionId}`, {
        method: "GET",
        headers: SECURITY_HEADERS,
    });
    if (!response.ok) throw new Error(`Failed to retrieve message logs for session: ${sessionId}`);
    return response.json();
}