"use client";

import { useEffect, useState } from "react";
import { DashboardStats } from "@/types/dashboard";

export default function DashboardPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchStats() {
            try {
                // Points directly to your updated FastAPI route endpoint layer
                const response = await fetch("http://localhost:8000/dashboard/stats", {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        // Include tenant headers or credentials here if required by dependencies
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to capture metrics matrix: ${response.status}`);
                }

                const data = await response.json();
                setStats(data);
            } catch (err: any) {
                console.error("Dashboard metric resolution failure:", err);
                setError(err.message || "Failed to load platform data analytics.");
            } finally {
                setLoading(false);
            }
        }

        fetchStats();
    }, []);

    return (
        <div className="space-y-6">

            {/* Top Welcome Context Panel */}
            <div className="border-b border-slate-900 pb-5">
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                    Enterprise RAG Platform
                </h1>
                <p className="mt-1.5 text-sm text-slate-400">
                    Internal Knowledge Assistant and Vector Engine Control Hub
                </p>
            </div>

            {/* Conditional Rendering Framework Block */}
            {loading ? (
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-32 w-full animate-pulse rounded-xl border border-slate-900 bg-slate-950/50" />
                    ))}
                </div>
            ) : error ? (
                <div className="rounded-xl border border-red-900/30 bg-red-950/20 p-4 text-xs font-mono text-red-400">
                    ⚠️ Operational Trace Error: {error}
                </div>
            ) : stats ? (

                /* RESPONSIVE FLUID METRIC CARD DECK */
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

                    <StatCard
                        title="Documents"
                        value={stats.documents}
                        icon="📂"
                        description="Indexed knowledge sources"
                    />

                    <StatCard
                        title="Chat Sessions"
                        value={stats.chat_sessions}
                        icon="🧠"
                        description="Active intelligence frameworks"
                    />

                    <StatCard
                        title="Messages"
                        value={stats.messages}
                        icon="💬"
                        description="Total pipeline transactions"
                    />

                </div>
            ) : null}

        </div>
    );
}

/* REUSABLE SUB-CARD LAYER IMPLEMENTATION */
interface StatCardProps {
    title: string;
    value: number;
    icon: string;
    description: string;
}

function StatCard({ title, value, icon, description }: StatCardProps) {
    return (
        <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 shadow-md transition-all hover:border-slate-800">
            <div className="flex items-center justify-between">
                <span className="text-slate-500 font-mono text-[10px] uppercase font-bold tracking-wider">
                    {title}
                </span>
                <span className="text-lg opacity-80" role="img" aria-label={title}>
                    {icon}
                </span>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
                <span className="text-3xl font-bold tracking-tight text-slate-100 font-mono">
                    {value.toLocaleString()}
                </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
                {description}
            </p>
        </div>
    );
}