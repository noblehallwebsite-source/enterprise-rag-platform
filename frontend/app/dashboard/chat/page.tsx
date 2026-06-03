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

    // Context Navigation and Relational Store States
    const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
    const [sessionsList, setSessionsList] = useState<ChatSessionPayload[]>([]);
    const [loadingSessions, setLoadingSessions] = useState(true);

    // Inline Session Mutation Tracking States
    const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
    const [editTitleBuffer, setEditTitleBuffer] = useState("");
    const renameInputRef = useRef<HTMLInputElement>(null);

    // Observability Infrastructure Filtering Configurations
    const [selectedService, setSelectedService] = useState<string | null>(null);
    const [selectedEnv, setSelectedEnv] = useState<string | null>(null);

    // 1. Initial Sync Hook: Hydrate past execution matrices from PostgreSQL
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

    // 2. Fixed Thread Selection Sync Hook: Pull logs on change boundaries
    useEffect(() => {
        if (!activeSessionId) {
            setMessages([]);
            return;
        }
        async function syncMessageChainLogs() {
            try {
                const logData = await fetchSessionHistory(activeSessionId!);

                // Explicitly check for the object structure matching your backend route
                if (logData && Array.isArray(logData.messages)) {
                    setMessages(logData.messages);
                } else if (Array.isArray(logData)) {
                    setMessages(logData);
                } else {
                    setMessages([]);
                }
            } catch (err) {
                console.error("Could not retrieve session interaction context blocks:", err);
                setMessages([]);
            }
        }
        syncMessageChainLogs();
    }, [activeSessionId]);

    // Focus utility handler for inline editing activations
    useEffect(() => {
        if (editingSessionId && renameInputRef.current) {
            renameInputRef.current.focus();
            renameInputRef.current.select();
        }
    }, [editingSessionId]);

    // 3. Mutate: Commit Text Title Change inline
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
            alert("Could not process name patch transformation.");
        } finally {
            setEditingSessionId(null);
        }
    }

    // 4. Mutate: Purge Data Session Record from Backend and UI State
    async function handlePurgeSession(e: React.MouseEvent, sessionId: string) {
        e.stopPropagation(); // Avoid triggering route context focus switches
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
            alert("Failed to drop session trace rows from backend registry database.");
        }
    }

    // 5. Orchestrate Inference Engine Streams
    async function askQuestion() {
        if (!question.trim() || loading) return;

        let targetSessionId = activeSessionId;
        const currentQuestionText = question.trim();
        setQuestion(""); // Instantly empty the input box to prevent double-submit hits

        // Auto-instantiate new session thread context row if running on clear canvas
        if (!targetSessionId) {
            try {
                setLoading(true);
                const generatedTitle = currentQuestionText.length > 25 ? `${currentQuestionText.slice(0, 25)}...` : currentQuestionText;
                const newSession = await createChatSession(generatedTitle);

                // Add the true session object with backend UUID to the local tracking array state
                setSessionsList(prev => [newSession, ...prev]);
                targetSessionId = newSession.id;
                setActiveSessionId(newSession.id);
            } catch (err) {
                console.error("Aborting stream: Auto-thread record instantiation failed:", err);
                setLoading(false);
                return;
            }
        }

        const userMessage: Message = { role: "user", content: currentQuestionText };
        setMessages((prev) => [...prev, userMessage]);
        setLoading(true);

        // Pre-allocate assistant chunk row response shell in state
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        try {
            const response = await fetch("http://164.68.120.179:8000/rag/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer dev-key-company-a"
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

            if (!response.ok) throw new Error(`Inference endpoint status error: ${response.status}`);
            if (!response.body) throw new Error("Network layer failed to allocate text-stream reader layer.");

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
                { role: "assistant", content: "A structural fault occurred while capturing streaming inference text output blocks." }
            ]);
        } finally {
            setLoading(false);
        }
    }

    if (!mounted) {
        return (
            <div className="p-6 font-sans text-slate-400 animate-pulse font-medium text-sm">
                Initializing local workspace context grids...
            </div>
        );
    }

    return (
        <div className="flex h-[calc(100vh-3.5rem)] w-full border border-slate-200/80 rounded-xl overflow-hidden bg-white shadow-xs font-sans">

            {/* SUB-SIDEBAR PANEL: Local chat thread navigation */}
            <div className="w-72 bg-slate-50 flex flex-col p-4 border-r border-slate-200/80">
                <button
                    onClick={() => { setActiveSessionId(null); setMessages([]); setQuestion(""); }}
                    disabled={loading || (activeSessionId === null && messages.length === 0)}
                    className="w-full py-2 px-4 mb-4 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-white text-slate-800 text-xs font-semibold rounded-lg border border-slate-200 shadow-xs transition-all flex items-center justify-center gap-2"
                >
                    ➕ Clear Canvas & New Chat
                </button>

                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 block px-1">
                    Workspace Threads
                </span>

                <div className="flex-1 overflow-y-auto space-y-1 pr-1 select-none">
                    {loadingSessions ? (
                        <div className="p-3 text-xs text-slate-400 italic animate-pulse">Querying database rows...</div>
                    ) : sessionsList.length === 0 ? (
                        <div className="p-3 text-xs text-slate-400 italic">No threads tracked under context scope.</div>
                    ) : (
                        sessionsList.map((session) => {
                            const isCurrent = session.id === activeSessionId;
                            const isEditing = session.id === editingSessionId;

                            return (
                                <div
                                    key={session.id}
                                    onClick={() => !loading && !isEditing && setActiveSessionId(session.id)}
                                    className={`group relative p-2 rounded-lg text-xs flex items-center justify-between border cursor-pointer transition-all ${isCurrent
                                        ? "bg-white text-slate-900 font-medium border-slate-200/80 shadow-xs"
                                        : "text-slate-500 hover:bg-slate-100/70 border-transparent hover:text-slate-800"
                                        } ${loading ? "pointer-events-none opacity-60" : ""}`}
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
                                            className="w-full p-1 bg-white border border-slate-300 rounded font-normal text-slate-800 focus:outline-none focus:border-slate-500"
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                    ) : (
                                        <>
                                            <span className="truncate pr-16 text-xs" title={session.title}>
                                                💬 {session.title}
                                            </span>

                                            {/* Context Operations: Rename / Delete buttons */}
                                            <div className="absolute right-1.5 opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity bg-transparent">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setEditingSessionId(session.id);
                                                        setEditTitleBuffer(session.title);
                                                    }}
                                                    title="Rename thread"
                                                    className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 rounded transition-colors"
                                                >
                                                    ✏️
                                                </button>
                                                <button
                                                    onClick={(e) => handlePurgeSession(e, session.id)}
                                                    title="Purge session records"
                                                    className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
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

            {/* CONSOLE DISPLAY WORKSPACE CANVAS */}
            <div className="flex-1 flex flex-col bg-slate-50/50">

                {/* Operational Filter Ribbon Toolbar */}
                <div className="p-4 bg-white border-b border-slate-200/60 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-4 text-xs">
                        <div className="flex items-center gap-1.5">
                            <label className="text-slate-400 font-medium">Vector Scope:</label>
                            <select
                                className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-600 font-medium focus:outline-none focus:border-slate-400"
                                onChange={(e) => setSelectedService(e.target.value || null)}
                                disabled={loading}
                            >
                                <option value="">All Vectors</option>
                                <option value="kubernetes">Cluster Logs Container</option>
                                <option value="hr-docs">Internal Assets Docs</option>
                            </select>
                        </div>

                        <div className="flex items-center gap-1.5">
                            <label className="text-slate-400 font-medium">Environment Context:</label>
                            <select
                                className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-600 font-medium focus:outline-none focus:border-slate-400"
                                onChange={(e) => setSelectedEnv(e.target.value || null)}
                                disabled={loading}
                            >
                                <option value="">Global Env</option>
                                <option value="production">Production Workloads</option>
                                <option value="staging">Staging Sandbox</option>
                            </select>
                        </div>
                    </div>

                    <div className="text-[10px] text-slate-400 font-mono bg-slate-50 border border-slate-200/40 px-2 py-1 rounded">
                        UUID: {activeSessionId ? activeSessionId.slice(0, 8) : "UNBOUND_WORKSPACE"}
                    </div>
                </div>

                {/* Conversation Output Core Grid */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs gap-1.5">
                            <div className="text-xl">🧠</div>
                            <div className="font-semibold text-slate-600 text-sm">Enterprise Prompt Canvas Ready</div>
                            <div className="max-w-xs text-center text-slate-400 leading-relaxed">
                                Enter an analytical deployment query. The thread transaction context mapping will link data blocks automatically.
                            </div>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`max-w-2xl p-4 rounded-xl text-xs leading-relaxed border transition-all ${msg.role === "user"
                                    ? "bg-slate-900 text-white ml-auto rounded-br-none border-slate-950 shadow-xs"
                                    : "bg-white text-slate-800 mr-auto rounded-bl-none border-slate-200/60 shadow-xs"
                                    }`}
                            >
                                <span className="block text-[8px] uppercase font-bold tracking-wider mb-1 opacity-50">
                                    {msg.role === "user" ? "Infrastructure Engineer" : "Cognition Engine Core"}
                                </span>
                                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                            </div>
                        ))
                    )}
                </div>

                {/* Question Input Controls Interface */}
                <div className="p-4 bg-white border-t border-slate-200/60 shadow-sm">
                    <div className="flex gap-2 max-w-3xl mx-auto">
                        <input
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && askQuestion()}
                            placeholder={loading ? "Extracting context embedding matrices..." : "Query infrastructure configuration matrices or security topology logs..."}
                            className="border border-slate-200 rounded-lg p-3 flex-1 text-xs bg-slate-50 focus:outline-none focus:bg-white focus:border-slate-400 transition-all disabled:opacity-60"
                            disabled={loading}
                        />
                        <button
                            onClick={askQuestion}
                            disabled={loading || !question.trim()}
                            className="px-5 py-3 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-xs transition-all disabled:opacity-40"
                        >
                            {loading ? "Processing..." : "Ask Core"}
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}