"use client";

import { useState, useEffect } from "react";

export default function ChatPage() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState("");
    const [mounted, setMounted] = useState(false);

    // Safely initialize session tracking state within client context layer
    useEffect(() => {
        setMounted(true);

        // Grabs or initializes the user conversational session state
        const existingSession = localStorage.getItem("rag_chat_session_id");
        if (existingSession) {
            setSessionId(existingSession);
        } else {
            const newSessionId = crypto.randomUUID();
            localStorage.setItem("rag_chat_session_id", newSessionId);
            setSessionId(newSessionId);
        }
    }, []);

    async function askQuestion() {
        if (!question.trim()) return;

        setLoading(true);
        setAnswer(""); // Flush state for clean incoming tokens

        try {
            // 🚀 FIXED PATH: Maps past Nginx straight to your FastAPI @router.post("/rag/stream")
            const response = await fetch("/api/rag/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    tenant_id: "company-a",
                    session_id: sessionId, // Dynamic user isolation token instance
                    query: question,
                    environment: null,
                    severity: null,
                    source: null,
                    service: null,
                }),
            });

            if (!response.body) {
                throw new Error("Target infrastructure failed to initialize streaming reader payload.");
            }

            // Initialize the lower-level chunk binary processing layout
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullText = "";

            // Stream evaluation processing loop
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                // Decode binary raw packet array chunk bytes to plain text tokens
                const chunk = decoder.decode(value, { stream: true });
                fullText += chunk;

                // Force react interface to draw incremental strings frame-by-frame
                setAnswer(fullText);
            }
        } catch (error) {
            console.error("Streaming Transaction Failure:", error);
            setAnswer("An infrastructure error occurred while streaming contextual generation. Check terminal logs.");
        } finally {
            setLoading(false);
        }
    }

    // Prevents Next.js layout compilation flickering due to localStorage checks
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

                {/* Active Session Badge indicator */}
                <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="font-mono" title={sessionId}>Session: {sessionId.slice(0, 8)}...</span>
                </div>
            </div>
            <p className="text-sm text-slate-500 mb-6">
                Interact with contextual memory architectures synced natively with your document vectors.
            </p>

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