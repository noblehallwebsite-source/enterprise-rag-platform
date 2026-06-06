"use client";

import { useEffect, useState } from "react";
import { DashboardStats } from "@/types/dashboard";

interface StatCardProps {
    title: string;
    value: number;
    icon: string;
    description: string;
}

function StatCard({
    title,
    value,
    icon,
    description,
}: StatCardProps) {
    return (
        <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 shadow-md hover:border-slate-800 transition-all">
            <div className="flex items-center justify-between">
                <span className="text-slate-500 font-mono text-[10px] uppercase font-bold tracking-wider">
                    {title}
                </span>

                <span
                    className="text-lg opacity-80"
                    role="img"
                    aria-label={title}
                >
                    {icon}
                </span>
            </div>

            <div className="mt-4">
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

export default function DashboardPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchStats() {
            try {
                setLoading(true);

                const response = await fetch(
                    "/api/dashboard/stats"
                );

                if (!response.ok) {
                    throw new Error(
                        `Failed to load dashboard metrics (${response.status})`
                    );
                }

                const data: DashboardStats =
                    await response.json();

                setStats(data);
            } catch (err) {
                console.error(
                    "Dashboard metric resolution failure:",
                    err
                );

                setError(
                    err instanceof Error
                        ? err.message
                        : "Failed to load dashboard metrics."
                );
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
                    Internal Knowledge Assistant and Vector Engine
                    Control Hub
                </p>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {[1, 2, 3, 4].map((item) => (
                        <div
                            key={item}
                            className="h-32 rounded-xl border border-slate-900 bg-slate-950/50 animate-pulse"
                        />
                    ))}
                </div>
            ) : error ? (
                <div className="rounded-xl border border-red-900/30 bg-red-950/20 p-4 text-red-400 text-xs font-mono">
                    ⚠️ Operational Trace Error: {error}
                </div>
            ) : stats ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
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

                    <StatCard
                        title="Tenants"
                        value={stats.tenants}
                        icon="🏢"
                        description="Registered organizations"
                    />
                </div>
            ) : null}
        </div>
    );
}