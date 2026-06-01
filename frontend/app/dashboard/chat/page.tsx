"use client";

import { useState, useEffect } from "react";

export default function ChatPage() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState("");
    const [mounted, setMounted] = useState(false);

    // Filter States to prevent vector space contamination
    const [selectedService, setSelectedService] = useState<string | null>(null);
    const [selectedEnv, setSelectedEnv] = useState<string | null>(null);

    useEffect(() => {
        setMounted(true);
        const existingSession = localStorage.getItem("rag_chat_session_id");
        if (existingSession) {
            setSessionId(existingSession);
        } else {
            let newSessionId = "";
            try {
                if (typeof window !== "undefined" && window.crypto && window.crypto.randomUUID) {
                    newSessionId = window.crypto.randomUUID();
                }
            } catch (e) {
                console.warn("Crypto API not available, switching to fallback identification.");
            }

            if (!newSessionId) {
                newSessionId = 'session-' + Math.random().toString(36).substring(2, 15) +
                    Math.random().toString(36).substring(2, 15);
            }
            localStorage.setItem("rag_chat_session_id", newSessionId);
            setSessionId(newSessionId);
        }
    }, []);

    async function askQuestion() {
        if (!question.trim()) return;

        setLoading(true);
        setAnswer("");

        try {
            const response = await fetch("/api/rag/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    tenant_id: "company-a",
                    session_id: sessionId,
                    query: question,
                    // 🚀 DYNAMIC METADATA FILTERS: Forces ChromaDB to strictly isolate documents
                    environment: selectedEnv,
                    severity: null,
                    source: null,
                    service: selectedService,
                }),
            });

            if (!response.body) {
                throw new Error("Target infrastructure failed to initialize streaming reader payload.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                fullText += chunk;
                setAnswer(fullText);
            }
        } catch (error) {
            console.error("Streaming Transaction Failure:", error);
            setAnswer("An infrastructure error occurred while streaming contextual generation.");
        } finally {
            setLoading(false);
        }
    }

    function resetConversation() {
        const newId = 'session-' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem("rag_chat_session_id", newId);
        setSessionId(newId);
        setAnswer("");
        setQuestion("");
    }

    if (!mounted) {
        return (
            <div className="max-w-5xl p-6 font-sans">
                <div className="animate-pulse text-slate-500 font-medium">
                    Syncing chat session registry layer...
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl p-6 font-sans">
            <div className="flex items-center justify-between mb-2">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">AI Knowledge Assistant</h1>

                <div className="flex items-center gap-3">
                    {/* Reset button to clear memory quickly */}
                    <button
                        onClick={resetConversation}
                        className="text-xs text-rose-600 bg-rose-50 border border-rose-200 hover:bg-rose-100 px-2.5 py-1 rounded-md transition-colors font-medium"
                    >
                        🔄 Reset Chat Memory
                    </button>

                    <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="font-mono">Session: {sessionId.slice(0, 8)}...</span>
                    </div>
                </div>
            </div>
            <p className="text-sm text-slate-500 mb-6">
                Interact with contextual memory architectures synced natively with your document vectors.
            </p>

            {/* 🛠️ NEW: META DATA FILTER WORKSPACE BAR */}
            <div className="mb-4 p-3 bg-slate-50 border border-slate-200 rounded-lg flex flex-wrap items-center gap-4 text-xs">
                <span className="font-semibold text-slate-500 uppercase tracking-wider">Target Scope Filters:</span>

                {/* Service Filter dropdown */}
                <div className="flex items-center gap-1.5">
                    <label className="text-slate-600 font-medium">Service:</label>
                    <select
                        className="bg-white border border-slate-300 rounded px-2 py-1 focus:outline-none focus:border-black"
                        onChange={(e) => setSelectedService(e.target.value || null)}
                    >
                        <option value="">All Services (No Filtering)</option>
                        <option value="kubernetes">Kubernetes Logs</option>
                        <option value="hr-docs">HR / Internal Documents</option>
                    </select>
                </div>

                {/* Environment Filter dropdown */}
                <div className="flex items-center gap-1.5">
                    <label className="text-slate-600 font-medium">Environment:</label>
                    <select
                        className="bg-white border border-slate-300 rounded px-2 py-1 focus:outline-none focus:border-black"
                        onChange={(e) => setSelectedEnv(e.target.value || null)}
                    >
                        <option value="">All Environments</option>
                        <option value="production">Production Only</option>
                        <option value="staging">Staging Only</option>
                    </select>
                </div>
            </div>

            {/* Input Group Block Layout */}
            <div className="flex gap-3 bg-slate-50 p-4 border border-slate-200 rounded-lg shadow-sm">
                <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !loading && askQuestion()}
                    placeholder="Ask a question concerning your enterprise infrastructure logs..."
                    className="border border-slate-300 rounded-md p-3 flex-1 text-sm bg-white focus:outline-none focus:border-slate-900 transition-colors"
                    disabled={loading}
                />
                <button
                    onClick={askQuestion}
                    disabled={loading || !question.trim()}
                    className="px-6 py-3 bg-black text-white text-sm font-medium rounded-md shadow hover:bg-slate-800 transition-colors disabled:opacity-50"
                >
                    {loading ? "Thinking..." : "Ask"}
                </button>
            </div>

            {/* Real-time Generative Yield Output Space */}
            <div className="mt-6 border border-slate-200 rounded-lg p-6 bg-white shadow-sm min-h-[250px] flex flex-col justify-between">
                <div className="whitespace-pre-wrap text-sm text-slate-800 leading-relaxed font-normal">
                    {answer || (
                        <span className="text-slate-400 italic">
                            Awaiting payload execution query parameter initialization...
                        </span>
                    )}
                </div>

                {loading && (
                    <div className="mt-4 flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest">
                        <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
                        <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
                        <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" />
                        Receiving live LLM token buffers
                    </div>
                )}
            </div>
        </div>
    );
}