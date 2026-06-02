// frontend/src/app/dashboard/chat/page.tsx
"use client";

import { useState, useEffect } from "react";
import {
    createChatSession,
    fetchAllSessions,
    fetchSessionHistory,
    ChatSessionPayload
} from "@/services/chat";

interface Message {
    role: "user" | "assistant";
    content: string;
}

export default function ChatPage() {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [mounted, setMounted] = useState(false);

    // SQL Database Session Tracking States
    const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
    const [sessionsList, setSessionsList] = useState<ChatSessionPayload[]>([]);
    const [loadingSessions, setLoadingSessions] = useState(true);

    // Observability Vector Filter Flags
    const [selectedService, setSelectedService] = useState<string | null>(null);
    const [selectedEnv, setSelectedEnv] = useState<string | null>(null);

    // 1. Initial Sync Hook: Sync historical list from PostgreSQL database
    useEffect(() => {
        setMounted(true);
        async function syncThreadHistoryRegistry() {
            try {
                const records = await fetchAllSessions();
                setSessionsList(records);

                // Fallback: Default directly to the most recent thread item if it exists
                if (records.length > 0) {
                    setActiveSessionId(records[0].id);
                }
            } catch (err) {
                console.error("Relational session sync operational failure:", err);
            } finally {
                setLoadingSessions(false);
            }
        }
        syncThreadHistoryRegistry();
    }, []);

    // 2. Thread Selection Sync Hook: Pull individual message logs when activeSessionId updates
    useEffect(() => {
        // Guard clause handles the null state immediately
        if (!activeSessionId) {
            setMessages([]);
            return;
        }

        // Local variable assignment isolates type context to strictly a string, 
        // satisfying TypeScript's strict null checking control flow.
        const sessionId: string = activeSessionId;

        async function syncMessageChainLogs() {
            try {
                const logData = await fetchSessionHistory(sessionId);
                setMessages(logData.messages);
            } catch (err) {
                console.error("Could not retrieve session interaction context blocks:", err);
                setMessages([]);
            }
        }
        syncMessageChainLogs();
    }, [activeSessionId]);

    // 3. Orchestrate Conversational Stream Interaction
    async function askQuestion() {
        if (!question.trim() || loading) return;

        let targetSessionId = activeSessionId;

        // Lazy-Initialization Guard: If a user types directly into an empty canvas screen, 
        // dynamically generate the underlying database session record first!
        if (!targetSessionId) {
            try {
                setLoading(true);
                const generatedTitle = question.length > 25 ? `${question.slice(0, 25)}...` : question;
                const newSession = await createChatSession(generatedTitle);
                setSessionsList(prev => [newSession, ...prev]);
                targetSessionId = newSession.id;
                setActiveSessionId(newSession.id);
            } catch (err) {
                console.error("Aborting stream: Auto-thread record instantiation failed:", err);
                alert("Failed to initialize conversational workspace environment context row.");
                setLoading(false);
                return;
            }
        }

        const userMessage: Message = { role: "user", content: question };
        setMessages((prev) => [...prev, userMessage]);
        setQuestion("");
        setLoading(true);

        // Prep downstream slot for upcoming streaming chunk additions
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        try {
            const response = await fetch("/api/rag/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": "dev-key-company-a"
                },
                body: JSON.stringify({
                    tenant_id: "company-a",
                    session_id: targetSessionId, // Links embedding response chains cleanly into SQL foreign keys
                    query: userMessage.content,
                    environment: selectedEnv || "",
                    severity: "",
                    source: "",
                    service: selectedService || "",
                }),
            });

            if (!response.ok) throw new Error(`Inference engine endpoint returned status error: ${response.status}`);
            if (!response.body) throw new Error("Network architecture failed to allocate text-stream reader layer.");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullAssistantText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                fullAssistantText += chunk;

                setMessages((prev) => {
                    const updated = [...prev];
                    if (updated.length > 0) {
                        updated[updated.length - 1] = { role: "assistant", content: fullAssistantText };
                    }
                    return updated;
                });
            }
        } catch (error) {
            console.error("Streaming Generation Error Stack:", error);
            setMessages((prev) => [
                ...prev.slice(0, -1),
                { role: "assistant", content: "An structural fault occurred while recording streaming inference data output blocks." }
            ]);
        } finally {
            setLoading(false);
        }
    }

    // 4. Client Explicit Trigger: Instantly reset view layout parameters for a fresh thread
    function startNewChat() {
        setActiveSessionId(null);
        setMessages([]);
        setQuestion("");
    }

    if (!mounted) {
        return (
            <div className="max-w-5xl p-6 font-sans text-slate-500 animate-pulse font-medium">
                Syncing chat history infrastructure engine...
            </div>
        );
    }

    return (
        <div className="flex h-[calc(100vh-4rem)] max-w-7xl mx-auto border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm font-sans">

            {/* LEFT SIDEBAR: Relational Thread History Navigation panel */}
            <div className="w-64 bg-slate-900 text-slate-200 flex flex-col p-4 border-r border-slate-800">
                <button
                    onClick={startNewChat}
                    disabled={loading || (activeSessionId === null && messages.length === 0)}
                    className="w-full py-2.5 px-4 mb-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-white text-sm font-medium rounded-lg border border-slate-700 transition-colors flex items-center justify-center gap-2 shadow-sm"
                >
                    ➕ New Chat
                </button>

                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 block px-2">
                    Persistent History
                </span>

                <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 select-none">
                    {loadingSessions ? (
                        <div className="p-3 text-xs text-slate-500 italic animate-pulse">Syncing thread rows...</div>
                    ) : sessionsList.length === 0 ? (
                        <div className="p-3 text-xs text-slate-500 italic">No historical entries stored.</div>
                    ) : (
                        sessionsList.map((session) => {
                            const isCurrent = session.id === activeSessionId;
                            return (
                                <div
                                    key={session.id}
                                    onClick={() => !loading && setActiveSessionId(session.id)}
                                    className={`p-2.5 rounded-md text-xs cursor-pointer truncate transition-all border ${isCurrent
                                        ? "bg-slate-800 text-white font-semibold border-slate-700 shadow-inner"
                                        : "text-slate-400 hover:bg-slate-850 hover:text-slate-200 border-transparent"
                                        } ${loading ? "pointer-events-none opacity-60" : ""}`}
                                    title={session.title}
                                >
                                    💬 {session.title}
                                </div>
                            );
                        })
                    )}
                </div>
            </div>

            {/* RIGHT MAIN WORKSPACE CONSOLE MONITOR */}
            <div className="flex-1 flex flex-col bg-slate-50">

                {/* Top Operational Telemetry Filter Toolbar */}
                <div className="p-4 bg-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-4 shadow-xs">
                    <div className="flex items-center gap-4 text-xs">
                        <div className="flex items-center gap-1.5">
                            <label className="text-slate-500 font-medium">Vector Space Scope:</label>
                            <select
                                className="bg-slate-50 border border-slate-200 rounded px-2.5 py-1 text-slate-700 font-medium focus:outline-none focus:border-slate-400"
                                onChange={(e) => setSelectedService(e.target.value || null)}
                                disabled={loading}
                            >
                                <option value="">All Scopes</option>
                                <option value="kubernetes">Cluster Logs Container</option>
                                <option value="hr-docs">Internal Assets Docs</option>
                            </select>
                        </div>

                        <div className="flex items-center gap-1.5">
                            <label className="text-slate-500 font-medium">Env Context:</label>
                            <select
                                className="bg-slate-50 border border-slate-200 rounded px-2.5 py-1 text-slate-700 font-medium focus:outline-none focus:border-slate-400"
                                onChange={(e) => setSelectedEnv(e.target.value || null)}
                                disabled={loading}
                            >
                                <option value="">All Environments</option>
                                <option value="production">Production Workloads</option>
                                <option value="staging">Staging Sandbox</option>
                            </select>
                        </div>
                    </div>

                    <div className="text-[10px] text-slate-400 font-mono bg-slate-50 border border-slate-100 px-2.5 py-1 rounded-md shadow-inner">
                        THREAD: {activeSessionId ? activeSessionId.slice(0, 8) : "UNSAVED_CANVAS"}
                    </div>
                </div>

                {/* Main Message Thread Timeline Stream */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400 text-sm gap-2">
                            <div className="text-2xl">🧠</div>
                            <div className="italic font-medium">Enterprise Knowledge Engine Ready</div>
                            <div className="text-xs text-slate-400 max-w-sm text-center">
                                Submit a question regarding infrastructure telemetry data. The execution context will instantly be bound to a persistent database session thread tracking log.
                            </div>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`max-w-3xl p-4 rounded-xl text-sm leading-relaxed border transition-all ${msg.role === "user"
                                    ? "bg-slate-900 text-white ml-auto rounded-br-none border-slate-950 shadow-sm"
                                    : "bg-white text-slate-800 mr-auto rounded-bl-none border-slate-200/80 shadow-xs"
                                    }`}
                            >
                                <span className="block text-[9px] uppercase font-bold tracking-wider mb-1.5 opacity-40">
                                    {msg.role === "user" ? "Infrastructure Engineer" : "System Cognition Core"}
                                </span>
                                <div className="whitespace-pre-wrap font-sans leading-relaxed">{msg.content}</div>
                            </div>
                        ))
                    )}
                </div>

                {/* Input Control Interface */}
                <div className="p-4 bg-white border-t border-slate-200 shadow-md">
                    <div className="flex gap-3 max-w-4xl mx-auto">
                        <input
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && askQuestion()}
                            placeholder={loading ? "Extracting context chunks and evaluating prompt parameters..." : "Query cluster log distributions or enterprise security architectures..."}
                            className="border border-slate-300 rounded-lg p-3.5 flex-1 text-sm bg-slate-50 focus:outline-none focus:bg-white focus:border-slate-900 transition-all disabled:opacity-60"
                            disabled={loading}
                        />
                        <button
                            onClick={askQuestion}
                            disabled={loading || !question.trim()}
                            className="px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-lg shadow transition-all disabled:opacity-40 disabled:hover:bg-slate-900"
                        >
                            {loading ? "Thinking..." : "Ask Core"}
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}