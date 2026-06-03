"use client";

import { useState, useEffect, useRef } from "react";
import {
    createChatSession,
    fetchAllSessions,
    fetchSessionHistory,
    renameChatSession,
    deleteChatSession,
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

    // Responsive Mobile Control Drawer
    const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

    // Inline Editing Tracking States
    const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
    const [editTitleBuffer, setEditTitleBuffer] = useState("");
    const renameInputRef = useRef<HTMLInputElement>(null);

    // Observability Vector Filter Flags
    const [selectedService, setSelectedService] = useState<string | null>(null);
    const [selectedEnv, setSelectedEnv] = useState<string | null>(null);

    const activeSessionIdRef = useRef<string | null>(null);
    const skipHistoryFetch = useRef(false);

    useEffect(() => {
        activeSessionIdRef.current = activeSessionId;
    }, [activeSessionId]);

    useEffect(() => {
        if (editingSessionId && renameInputRef.current) {
            renameInputRef.current.focus();
            renameInputRef.current.select();
        }
    }, [editingSessionId]);

    // 1. Initial Sync Hook
    useEffect(() => {
        setMounted(true);
        async function syncThreadHistoryRegistry() {
            try {
                const records = await fetchAllSessions();
                setSessionsList(records || []);
                if (records && records.length > 0) {
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

    // 2. Thread Selection Sync Hook
    useEffect(() => {
        if (!activeSessionId) {
            setMessages([]);
            return;
        }

        if (skipHistoryFetch.current) {
            skipHistoryFetch.current = false;
            return;
        }

        const sessionId: string = activeSessionId;

        async function syncMessageChainLogs() {
            try {
                const logData = await fetchSessionHistory(sessionId);
                if (sessionId !== activeSessionIdRef.current) return;

                if (logData && logData.messages) {
                    setMessages(logData.messages);
                } else if (Array.isArray(logData)) {
                    setMessages(logData);
                } else {
                    setMessages([]);
                }
            } catch (err) {
                console.error("Could not retrieve session interaction context blocks:", err);
                if (sessionId === activeSessionIdRef.current) setMessages([]);
            }
        }
        syncMessageChainLogs();
    }, [activeSessionId]);

    // 3. Orchestrate Conversational Stream Interaction
    async function askQuestion() {
        if (!question.trim() || loading) return;

        let targetSessionId = activeSessionId;
        const currentQuestionText = question.trim();

        setQuestion("");
        setLoading(true);

        if (!targetSessionId) {
            try {
                const generatedTitle = currentQuestionText.length > 25 ? `${currentQuestionText.slice(0, 25)}...` : currentQuestionText;
                skipHistoryFetch.current = true;

                const newSession = await createChatSession(generatedTitle);
                setSessionsList(prev => [newSession, ...prev]);
                targetSessionId = newSession.id;
                setActiveSessionId(newSession.id);
            } catch (err) {
                console.error("Aborting stream: Auto-thread record instantiation failed:", err);
                skipHistoryFetch.current = false;
                setLoading(false);
                return;
            }
        }

        const userMessage: Message = { role: "user", content: currentQuestionText };
        setMessages((prev) => [...prev, userMessage, { role: "assistant", content: "" }]);

        try {
            const response = await fetch("/api/rag/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": "dev-key-company-a"
                },
                body: JSON.stringify({
                    tenant_id: "company-a",
                    session_id: targetSessionId,
                    query: userMessage.content,
                    environment: selectedEnv || "",
                    severity: "",
                    source: "",
                    service: selectedService || "",
                }),
            });

            if (!response.ok) throw new Error(`Stream endpoint returned error: ${response.status}`);
            if (!response.body) throw new Error("Failed to allocate text-stream reader layer.");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullAssistantText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                fullAssistantText += chunk;

                if (targetSessionId === activeSessionIdRef.current) {
                    setMessages((prev) => {
                        const updated = [...prev];
                        if (updated.length > 0) {
                            updated[updated.length - 1] = { role: "assistant", content: fullAssistantText };
                        }
                        return updated;
                    });
                }
            }
        } catch (error) {
            console.error("Streaming Generation Error Stack:", error);
            if (targetSessionId === activeSessionIdRef.current) {
                setMessages((prev) => [
                    ...prev.slice(0, -1),
                    { role: "assistant", content: "A structural fault occurred while recording streaming inference data output blocks." }
                ]);
            }
        } finally {
            setLoading(false);
        }
    }

    async function handleRenameCommit(sessionId: string) {
        if (!editTitleBuffer.trim()) {
            setEditingSessionId(null);
            return;
        }
        try {
            const updated = await renameChatSession(sessionId, editTitleBuffer.trim());
            setSessionsList(prev => prev.map(s => s.id === sessionId ? { ...s, title: updated.title } : s));
        } catch (err) {
            console.error("Failed to commit inline title modification:", err);
        } finally {
            setEditingSessionId(null);
        }
    }

    async function handlePurgeSession(e: React.MouseEvent, sessionId: string) {
        e.stopPropagation();
        if (!confirm("Are you sure you want to permanently delete this chat history thread?")) return;

        try {
            await deleteChatSession(sessionId);
            setSessionsList(prev => prev.filter(s => s.id !== sessionId));
            if (activeSessionId === sessionId) {
                setActiveSessionId(null);
                setMessages([]);
            }
        } catch (err) {
            console.error("Failed to execute data entity clear operation:", err);
        }
    }

    function startNewChat() {
        setActiveSessionId(null);
        setMessages([]);
        setQuestion("");
        setIsMobileSidebarOpen(false);
    }

    if (!mounted) {
        return (
            <div className="flex h-screen items-center justify-center bg-slate-900 text-sm font-medium text-slate-400 font-sans">
                <div className="flex items-center gap-3">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-500 border-t-transparent" />
                    Syncing console environment infrastructure...
                </div>
            </div>
        );
    }

    // Extracted Sidebar component to avoid duplicate layout declarations
    const SidebarContent = () => (
        <div className="flex h-full flex-col bg-slate-950 p-4 text-slate-200">
            <button
                onClick={startNewChat}
                disabled={loading || (activeSessionId === null && messages.length === 0)}
                className="mb-6 flex w-full items-center justify-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-4 py-2.5 text-xs font-semibold tracking-wide text-white transition-all hover:bg-slate-850 active:scale-[0.98] disabled:opacity-30"
            >
                <span>➕</span> New Terminal Context
            </button>

            <span className="mb-3 block px-2 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                Persistent Threads
            </span>

            <div className="flex-1 space-y-1 overflow-y-auto pr-1 select-none custom-scrollbar">
                {loadingSessions ? (
                    <div className="p-3 text-xs italic text-slate-600 animate-pulse">Syncing catalog registry...</div>
                ) : sessionsList.length === 0 ? (
                    <div className="p-3 text-xs italic text-slate-600">No telemetry frames allocated.</div>
                ) : (
                    sessionsList.map((session) => {
                        const isCurrent = session.id === activeSessionId;
                        const isEditing = session.id === editingSessionId;

                        return (
                            <div
                                key={session.id}
                                onClick={() => {
                                    if (!loading && !isEditing) {
                                        setActiveSessionId(session.id);
                                        setIsMobileSidebarOpen(false);
                                    }
                                }}
                                className={`group relative flex items-center justify-between rounded-lg p-3 text-xs border transition-all duration-150 ${isCurrent
                                    ? "bg-slate-900 text-white font-medium border-slate-800 shadow-sm"
                                    : "text-slate-400 border-transparent hover:bg-slate-900/40 hover:text-slate-200"
                                    } ${loading ? "pointer-events-none opacity-50" : ""}`}
                            >
                                {isEditing ? (
                                    <input
                                        ref={renameInputRef}
                                        value={editTitleBuffer}
                                        onChange={(e) => setEditTitleBuffer(e.target.value)}
                                        onBlur={() => handleRenameCommit(session.id)}
                                        onKeyDown={(e) => {
                                            if (e.key === "Enter") handleRenameCommit(session.id);
                                            if (e.key === "Escape") setEditingSessionId(null);
                                        }}
                                        className="w-full bg-slate-950 px-2 py-1 border border-slate-700 rounded text-slate-200 focus:outline-none focus:border-slate-500"
                                        onClick={(e) => e.stopPropagation()}
                                    />
                                ) : (
                                    <>
                                        <span className="truncate pr-16" title={session.title}>
                                            📟 {session.title}
                                        </span>

                                        <div className="absolute right-2 flex items-center gap-1 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity duration-150">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setEditingSessionId(session.id);
                                                    setEditTitleBuffer(session.title);
                                                }}
                                                className="p-1 text-slate-500 hover:text-white rounded bg-slate-950/80 lg:bg-transparent"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                onClick={(e) => handlePurgeSession(e, session.id)}
                                                className="p-1 text-slate-500 hover:text-red-400 rounded bg-slate-950/80 lg:bg-transparent"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );

    return (
        <div className="flex h-screen w-full overflow-hidden bg-slate-900 font-sans text-slate-900 selection:bg-slate-200">

            {/* DESKTOP SIDEBAR PANEL */}
            <aside className="hidden w-64 shrink-0 border-r border-slate-800 lg:block">
                <SidebarContent />
            </aside>

            {/* RESPONSIVE MOBILE OVERLAY SIDEBAR DRAWER */}
            {isMobileSidebarOpen && (
                <div
                    className="fixed inset-0 z-50 flex bg-slate-950/60 backdrop-blur-xs lg:hidden"
                    onClick={() => setIsMobileSidebarOpen(false)}
                >
                    <div
                        className="w-72 h-full animate-slide-in"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <SidebarContent />
                    </div>
                </div>
            )}

            {/* MAIN APP CONSOLE MONITOR VIEWPORT */}
            <main className="flex flex-1 flex-col overflow-hidden bg-slate-950 lg:m-2 lg:rounded-2xl lg:border lg:border-slate-800 shadow-2xl">

                {/* Global Telemetry Control Header Bar */}
                <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-800/60 bg-slate-900/40 px-4 backdrop-blur-md">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsMobileSidebarOpen(true)}
                            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 text-slate-400 hover:bg-slate-900 lg:hidden"
                        >
                            ☰
                        </button>

                        <div className="flex flex-wrap items-center gap-2 sm:gap-4">
                            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
                                <span>Scope:</span>
                                <select
                                    className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-300 focus:outline-none focus:border-slate-600 text-xs cursor-pointer"
                                    onChange={(e) => setSelectedService(e.target.value || null)}
                                    disabled={loading}
                                    value={selectedService || ""}
                                >
                                    <option value="">All Scopes</option>
                                    <option value="kubernetes">Cluster Logs Container</option>
                                    <option value="hr-docs">Internal Assets Docs</option>
                                </select>
                            </div>

                            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
                                <span>Env:</span>
                                <select
                                    className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-300 focus:outline-none focus:border-slate-600 text-xs cursor-pointer"
                                    onChange={(e) => setSelectedEnv(e.target.value || null)}
                                    disabled={loading}
                                    value={selectedEnv || ""}
                                >
                                    <option value="">All Environments</option>
                                    <option value="production">Production Workloads</option>
                                    <option value="staging">Staging Sandbox</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="hidden sm:block rounded-md border border-slate-800 bg-slate-950 px-2.5 py-1 font-mono text-[10px] tracking-tight text-slate-500 shadow-inner">
                        ID: {activeSessionId ? activeSessionId.slice(0, 8) : "UNSAVED_CANVAS"}
                    </div>
                </header>

                {/* Core Message Timeline Content Deck */}
                <div className="flex-1 overflow-y-auto bg-slate-900/20 p-4 md:p-6 space-y-6 custom-scrollbar">
                    {messages.length === 0 ? (
                        <div className="flex h-full flex-col items-center justify-center text-center px-4">
                            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl border border-slate-800 bg-slate-900 text-xl shadow-inner animate-pulse">
                                🧠
                            </div>
                            <h3 className="text-sm font-semibold tracking-wide text-slate-200">System Cognition Core Engaged</h3>
                            <p className="mt-1 max-w-sm text-xs leading-normal text-slate-500">
                                Submit execution queries down into the orchestration pipeline layer. Telemetry vectors wrap completely inside managed persistence arrays automatically.
                            </p>
                        </div>
                    ) : (
                        <div className="mx-auto max-w-3xl space-y-6">
                            {messages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex w-full flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
                                >
                                    <div className="mb-1 text-[9px] font-bold uppercase tracking-widest text-slate-500 px-1">
                                        {msg.role === "user" ? "Infrastructure Engineer" : "Cognition Core Output"}
                                    </div>
                                    <div
                                        className={`w-full max-w-2xl rounded-xl border p-4 text-xs leading-relaxed shadow-xs transition-all ${msg.role === "user"
                                            ? "bg-slate-100 text-slate-900 border-slate-200"
                                            : "bg-slate-900 text-slate-100 border-slate-800/80"
                                            }`}
                                    >
                                        <div className="whitespace-pre-wrap font-mono leading-relaxed">{msg.content}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Bottom Input Execution Interface Console Box */}
                <footer className="shrink-0 border-t border-slate-800/60 bg-slate-900/20 p-4">
                    <div className="mx-auto flex max-w-3xl items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 p-1.5 focus-within:border-slate-700 transition-colors">
                        <input
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && askQuestion()}
                            placeholder={loading ? "Evaluating execution trace vector buffers..." : "Query cluster logs or security parameters..."}
                            className="flex-1 bg-transparent px-3 py-2 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none disabled:opacity-50"
                            disabled={loading}
                        />
                        <button
                            onClick={askQuestion}
                            disabled={loading || !question.trim()}
                            className="flex h-9 items-center justify-center rounded-lg bg-white px-4 text-xs font-semibold tracking-wide text-slate-950 transition-all hover:bg-slate-200 active:scale-[0.97] disabled:bg-slate-900 disabled:text-slate-700 disabled:pointer-events-none"
                        >
                            {loading ? "Processing..." : "Execute"}
                        </button>
                    </div>
                </footer>

            </main>
        </div>
    );
}