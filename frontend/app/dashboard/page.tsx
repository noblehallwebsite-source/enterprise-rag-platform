"use client";

import { useEffect, useState } from "react";

// Update your local TypeScript validation boundary layout structure
interface DashboardStats {
    documents: number;
    chat_sessions: number;
    messages: number;
    tenants: number;
    success_rate: number;   // 🚀 Added
    avg_latency: number;    // 🚀 Added
    total_requests: number; // 🚀 Added
}

interface StatCardProps {
    title: string;
    value: string | number;
    icon: string;
    description: string;
}

function StatCard({ title, value, icon, description }: StatCardProps) {
    return (
        <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 shadow-md hover:border-slate-800 transition-all">
            <div className="flex items-center justify-between">
                <span className="text-slate-500 font-mono text-[10px] uppercase font-bold tracking-wider">
                    {title}
                </span>
                <span className="text-lg opacity-80" role="img" aria-label={title}>
                    {icon}
                </span>
            </div>
            <div className="mt-4">
                <span className="text-3xl font-bold tracking-tight text-slate-100 font-mono">
                    {value}
                </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
                {description}
            </p>
        </div>
    );
}

export default function DashboardPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchStats() {
            try {
                setLoading(true);
                const response = await fetch("/api/dashboard/stats");
                if (!response.ok) throw new Error(`Failed to load metrics (${response.status})`);
                const data: DashboardStats = await response.json();
                setStats(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load metrics.");
            } finally {
                setLoading(false);
            }
        }
        fetchStats();
    }, []);

    return (
        <div className="space-y-6">
            <div className="border-b border-slate-900 pb-5">
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                    Enterprise RAG Platform
                </h1>
                <p className="mt-1.5 text-sm text-slate-400">
                    Internal Knowledge Assistant and Vector Engine Control Hub
                </p>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map((item) => (
                        <div key={item} className="h-32 rounded-xl border border-slate-900 bg-slate-950/50 animate-pulse" />
                    ))}
                </div>
            ) : error ? (
                <div className="rounded-xl border border-red-900/30 bg-red-950/20 p-4 text-red-400 text-xs font-mono">
                    ⚠️ Operational Trace Error: {error}
                </div>
            ) : stats ? (
                // 📊 Expanded 6-Card High-Performance System Grid Layout
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    <StatCard title="Total Requests" value={stats.total_requests.toLocaleString()} icon="⚡" description="Total incoming execution triggers" />
                    <StatCard title="Pipeline Accuracy" value={`${stats.success_rate}%`} icon="🎯" description="Successful prompt execution matrix ratio" />
                    <StatCard title="Avg Latency" value={`${stats.avg_latency}s`} icon="⏱️" description="Average completion transaction roundtrip" />
                    <StatCard title="Documents" value={stats.documents.toLocaleString()} icon="📂" description="Indexed knowledge sources" />
                    <StatCard title="Chat Sessions" value={stats.chat_sessions.toLocaleString()} icon="🧠" description="Active intelligence frameworks" />
                    <StatCard title="Messages" value={stats.messages.toLocaleString()} icon="💬" description="Total pipeline transactions" />
                </div>
            ) : null}
        </div>
    );
}