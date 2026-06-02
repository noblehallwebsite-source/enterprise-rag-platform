// frontend/src/app/dashboard/chat/page.tsx
"use client";

import { useState, useEffect } from "react";
import axios from "axios";

interface Message {
    role: "user" | "assistant";
    content: string;
}

export default function ChatPage() {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState("");
    const [historySessions, setHistorySessions] = useState<string[]>([]);
    const [mounted, setMounted] = useState(false);

    // Filter States to prevent vector space contamination
    const [selectedService, setSelectedService] = useState<string | null>(null);
    const [selectedEnv, setSelectedEnv] = useState<string | null>(null);

    // Common security authorization context config block
    const GATEWAY_HEADERS = {
        "Content-Type": "application/json",
        "x-api-key": "dev-key-company-a" // Enforces secure platform validation
    };

    // 1. Core Lifecycle Initialization
    useEffect(() => {
        setMounted(true);

        const savedSessionsJson = localStorage.getItem("rag_all_sessions");
        let sessionsList: string[] = savedSessionsJson ? JSON.parse(savedSessionsJson) : [];

        const activeSession = localStorage.getItem("rag_chat_session_id");

        if (activeSession) {
            setSessionId(activeSession);
            if (!sessionsList.includes(activeSession)) {
                sessionsList.unshift(activeSession);
            }
        } else {
            const newSessionId = "session-" + Math.random().toString(36).substring(2, 15);
            localStorage.setItem("rag_chat_session_id", newSessionId);
            setSessionId(newSessionId);
            sessionsList.unshift(newSessionId);
        }

        localStorage.setItem("rag_all_sessions", JSON.stringify(sessionsList));
        setHistorySessions(sessionsList);
    }, []);

    // 2. Fetch Chat History from Backend when Session Changes
    useEffect(() => {
        if (!sessionId) return;

        async function fetchSessionHistory() {
            try {
                // Injects standard API authentication token structure to past logs query loop
                const response = await axios.get(`/api/chat/history/${sessionId}`, {
                    headers: { "x-api-key": "dev-key-company-a" }
                });
                if (response.data && response.data.messages) {
                    setMessages(response.data.messages);
                } else {
                    setMessages([]);
                }
            } catch (err) {
                console.warn("Backend chat history lookup bypassed or unconfigured for active token sandbox. Initializing empty history.");
                setMessages([]);
            }
        }

        fetchSessionHistory();
    }, [sessionId]);

    // 3. Handle Streaming Response
    async function askQuestion() {
        if (!question.trim() || loading) return;

        const userMessage: Message = { role: "user", content: question };
        setMessages((prev) => [...prev, userMessage]);
        setQuestion("");
        setLoading(true);

        // Prepare a blank slot in the array for the upcoming live text streaming tokens
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        try {
            const response = await fetch("/api/rag/stream", {
                method: "POST",
                headers: GATEWAY_HEADERS,
                body: JSON.stringify({
                    tenant_id: "company-a",
                    session_id: sessionId,
                    query: userMessage.content,
                    // Map parameters dynamically to support ChromaDB indexing type validation blocks
                    environment: selectedEnv || "",
                    severity: "",
                    source: "",
                    service: selectedService || "",
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP Stream Initialization Aborted: Status ${response.status}`);
            }

            if (!response.body) throw new Error("Failed to initialize stream reader engine.");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullAssistantText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                fullAssistantText += chunk;

                // Dynamically update ONLY the last item in the message log array (the assistant response)
                setMessages((prev) => {
                    const updated = [...prev];
                    if (updated.length > 0) {
                        updated[updated.length - 1] = { role: "assistant", content: fullAssistantText };
                    }
                    return updated;
                });
            }
        } catch (error) {
            console.error("Streaming Transaction Failure:", error);
            setMessages((prev) => [
                ...prev.slice(0, -1),
                { role: "assistant", content: "An operational fault occurred while attempting to stream contextual inference content." }
            ]);
        } finally {
            setLoading(false);
        }
    }

    // 4. Spawns a completely new conversation thread
    function startNewChat() {
        const newId = "session-" + Math.random().toString(36).substring(2, 15);
        localStorage.setItem("rag_chat_session_id", newId);

        const updatedSessions = [newId, ...historySessions];
        localStorage.setItem("rag_all_sessions", JSON.stringify(updatedSessions));

        setHistorySessions(updatedSessions);
        setSessionId(newId);
        setMessages([]);
        setQuestion("");
    }

    // 5. Switch Active Conversational Line Context
    function switchSession(id: string) {
        if (loading) return; // Prevent navigation lock during active mutations
        localStorage.setItem("rag_chat_session_id", id);
        setSessionId(id);
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

            {/* LEFT SIDEBAR: ChatGPT Conversational History Register */}
            <div className="w-64 bg-slate-900 text-slate-200 flex flex-col p-4 border-r border-slate-800">
                <button
                    onClick={startNewChat}
                    disabled={loading}
                    className="w-full py-2.5 px-4 mb-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg border border-slate-700 transition-colors flex items-center justify-center gap-2"
                >
                    ➕ New Chat
                </button>

                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 block px-2">
                    Past Conversations
                </span>

                <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 select-none">
                    {historySessions.map((id) => (
                        <div
                            key={id}
                            onClick={() => switchSession(id)}
                            className={`p-2.5 rounded-md text-xs font-mono cursor-pointer truncate transition-all ${id === sessionId
                                ? "bg-slate-800 text-white font-semibold shadow-inner border border-slate-700"
                                : "text-slate-400 hover:bg-slate-850 hover:text-slate-200"
                                } ${loading ? "pointer-events-none opacity-60" : ""}`}
                            title={id}
                        >
                            💬 {id.slice(0, 16)}...
                        </div>
                    ))}
                </div>
            </div>

            {/* RIGHT MAIN CHAT SCREEN MONITOR */}
            <div className="flex-1 flex flex-col bg-slate-50">

                {/* Top Operational Telemetry Dashboard Bar */}
                <div className="p-4 bg-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4 text-xs">
                        <div className="flex items-center gap-1.5">
                            <label className="text-slate-500 font-medium">Service:</label>
                            <select
                                className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-none focus:border-slate-400"
                                onChange={(e) => setSelectedService(e.target.value || null)}
                                disabled={loading}
                            >
                                <option value="">All Services</option>
                                <option value="kubernetes">Kubernetes Logs</option>
                                <option value="hr-docs">HR / Internal Documents</option>
                            </select>
                        </div>

                        <div className="flex items-center gap-1.5">
                            <label className="text-slate-500 font-medium">Env:</label>
                            <select
                                className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-none focus:border-slate-400"
                                onChange={(e) => setSelectedEnv(e.target.value || null)}
                                disabled={loading}
                            >
                                <option value="">All Environments</option>
                                <option value="production">Production Only</option>
                                <option value="staging">Staging Only</option>
                            </select>
                        </div>
                    </div>

                    <div className="text-[11px] text-slate-400 font-mono bg-slate-50 border border-slate-100 px-2 py-0.5 rounded">
                        ID: {sessionId}
                    </div>
                </div>

                {/* Message Thread Stream Wrapper */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 ? (
                        <div className="h-full flex items-center justify-center text-slate-400 text-sm italic">
                            Awaiting query parameters initialization... Ask a question below.
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`max-w-3xl p-4 rounded-xl text-sm leading-relaxed ${msg.role === "user"
                                    ? "bg-slate-900 text-white ml-auto rounded-br-none shadow-sm"
                                    : "bg-white border border-slate-200 text-slate-800 mr-auto rounded-bl-none shadow-xs"
                                    }`}
                            >
                                <span className="block text-[10px] uppercase font-bold tracking-wider mb-1 opacity-40">
                                    {msg.role === "user" ? "You" : "AI Knowledge Engine"}
                                </span>
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                            </div>
                        ))
                    )}
                </div>

                {/* Dynamic Input Bar Panel Layout */}
                <div className="p-4 bg-white border-t border-slate-200">
                    <div className="flex gap-3 max-w-4xl mx-auto">
                        <input
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && askQuestion()}
                            placeholder={loading ? "Generating answers from cluster embeddings..." : "Ask a question concerning your enterprise infrastructure logs..."}
                            className="border border-slate-300 rounded-lg p-3 flex-1 text-sm bg-slate-50 focus:outline-none focus:bg-white focus:border-slate-900 transition-all disabled:opacity-60"
                            disabled={loading}
                        />
                        <button
                            onClick={askQuestion}
                            disabled={loading || !question.trim()}
                            className="px-6 py-3 bg-black text-white text-sm font-medium rounded-lg shadow hover:bg-slate-800 transition-colors disabled:opacity-45"
                        >
                            {loading ? "Thinking..." : "Ask"}
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}