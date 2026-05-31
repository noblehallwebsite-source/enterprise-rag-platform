"use client";

import { useState } from "react";
import axios from "axios";

export default function SearchPage() {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<any[]>([]);
    const [hasSearched, setHasSearched] = useState(false);

    async function handleSearch() {
        if (!query.trim()) return;

        try {
            setLoading(true);
            setHasSearched(true);

            // 🚀 Clean relative path routes past Nginx directly to your FastAPI /search endpoint
            const response = await axios.post("/api/search", {
                tenant_id: "company-a", // Linked seamlessly to your Nginx injected header validation
                query: query,
                environment: null,
                severity: null,
                source: null,
                service: null
            });

            // Maps the array returned by search_documents inside ChromaDB
            setResults(response.data.results || []);
        } catch (error) {
            console.error("Semantic Query Execution Fault:", error);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="max-w-4xl p-6 font-sans">
            <h1 className="text-3xl font-bold mb-2 tracking-tight text-slate-900">Semantic Search</h1>
            <p className="text-sm text-slate-500 mb-6">
                Query your multi-tenant knowledge base using AI-powered vector space matching.
            </p>

            {/* Search Input Bar Group */}
            <div className="flex gap-3 bg-slate-50 p-4 border border-slate-200 rounded-lg shadow-sm">
                <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Ask something (e.g., 'Why are workloads crashing?' or 'production outage')..."
                    className="border border-slate-300 rounded-md p-3 flex-1 text-sm bg-white focus:outline-none focus:border-slate-900 transition-colors"
                />
                <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="px-6 py-3 bg-black text-white text-sm font-medium rounded-md shadow hover:bg-slate-800 transition-colors disabled:opacity-50"
                >
                    {loading ? "Searching..." : "Search"}
                </button>
            </div>

            {loading && (
                <div className="mt-8 space-y-4">
                    {[1, 2].map((n) => (
                        <div key={n} className="animate-pulse bg-slate-50 border border-slate-200 rounded-lg p-5 h-28" />
                    ))}
                </div>
            )}

            {/* Search Results Workspace */}
            {!loading && (
                <div className="mt-8 space-y-4">
                    {results.map((item, index) => {
                        // Safe extraction of the metadata dictionary inside your Chroma document model
                        const meta = item.metadata || {};

                        return (
                            <div key={index} className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm hover:border-slate-300 transition-all">
                                {/* The Extracted Text Fragment */}
                                <p className="text-sm text-slate-800 leading-relaxed font-normal mb-4 break-words">
                                    "{item.text}"
                                </p>

                                <hr className="border-slate-100 my-3" />

                                {/* Enterprise Metadata Badges Grid */}
                                <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
                                    <div className="flex flex-wrap items-center gap-2">
                                        {/* Service Block */}
                                        <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded border border-slate-200 font-medium">
                                            <span className="text-slate-400 font-normal">Service:</span> {meta.service || "unknown"}
                                        </span>

                                        {/* Environment Block */}
                                        <span className={`px-2 py-1 rounded border font-medium ${meta.environment === "production"
                                            ? "bg-amber-50 text-amber-800 border-amber-200"
                                            : "bg-slate-100 text-slate-700 border-slate-200"
                                            }`}>
                                            <span className="opacity-60 font-normal">Env:</span> {meta.environment || "unknown"}
                                        </span>

                                        {/* Severity Block */}
                                        <span className={`px-2 py-1 rounded border font-medium ${meta.severity === "critical" || meta.severity === "high"
                                            ? "bg-rose-50 text-rose-800 border-rose-200"
                                            : "bg-slate-100 text-slate-700 border-slate-200"
                                            }`}>
                                            <span className="opacity-60 font-normal">Severity:</span> {meta.severity || "unknown"}
                                        </span>

                                        {/* Source Filename Track */}
                                        <span className="text-slate-400 max-w-xs truncate" title={meta.original_filename || meta.source}>
                                            📂 {meta.original_filename || meta.source || "Ingested Payload"}
                                        </span>
                                    </div>

                                    {/* Mathematical Similarity Metric */}
                                    <div className="font-mono text-slate-400 text-[11px] bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                                        Vector Distance: <span className="text-slate-600 font-semibold">{Number(item.distance).toFixed(4)}</span>
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {/* Empty State Feedback */}
                    {hasSearched && results.length === 0 && (
                        <div className="text-center py-12 border border-dashed border-slate-200 rounded-lg text-slate-400 text-sm">
                            No matching context fragments found inside the tenant workspace database.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}