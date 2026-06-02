// frontend/src/app/dashboard/documents/page.tsx
"use client";

import { useEffect, useState } from "react";
import { Document } from "@/types/document";
import { getDocuments, deleteDocument } from "@/services/documents";

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    // Track row-level deletion loading states by storing document IDs
    const [deletingIds, setDeletingIds] = useState<Record<string, boolean>>({});

    async function loadDocuments() {
        try {
            const data = await getDocuments();
            setDocuments(data);
        } catch (error) {
            console.error("Failed fetching documents telemetry registry:", error);
        } finally {
            setLoading(false);
        }
    }

    // Handles real-time syncing and interval component state teardown
    useEffect(() => {
        loadDocuments();

        const interval = setInterval(loadDocuments, 5000);

        return () => clearInterval(interval);
    }, []);

    // Handles cascading multi-tenant document deletion
    async function handleDelete(documentId: string, filename: string) {
        if (!confirm(`Are you sure you want to permanently drop "${filename}" and all associated vector chunks from ChromaDB?`)) {
            return;
        }

        try {
            // Set row-specific loading boundary
            setDeletingIds(prev => ({ ...prev, [documentId]: true }));

            await deleteDocument(documentId);

            // Optimistic UI state update for instant, snappy user feedback
            setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        } catch (error) {
            console.error("Deletion lifecycle failure:", error);
            alert("Critical Error: Failed to cleanly evict document fragments from the backend layers.");
        } finally {
            // Clean up row lifecycle boundary
            setDeletingIds(prev => {
                const updated = { ...prev };
                delete updated[documentId];
                return updated;
            });
        }
    }

    // Status Color Custom Mapper
    const getStatusBadge = (status: string) => {
        switch (status) {
            case "COMPLETED":
                return "bg-green-50 border-green-200 text-green-700";
            case "PROCESSING":
                return "bg-amber-50 border-amber-200 text-amber-700 animate-pulse";
            case "FAILED":
                return "bg-red-50 border-red-200 text-red-700";
            default:
                return "bg-gray-50 border-gray-200 text-gray-700";
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-gray-500 text-sm font-medium animate-pulse">
                    Loading enterprise ingestion registry...
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-gray-900">
                        Documents Engine
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Real-time multi-tenant data ingestion tracking and chunk metrics.
                    </p>
                </div>
                <div className="flex items-center gap-2 text-xs font-medium text-gray-400 bg-gray-50 px-3 py-1.5 rounded-md border border-gray-100 self-start md:self-auto">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                    Auto-refreshing every 5s
                </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left border-collapse">
                        <thead>
                            <tr className="border-b border-gray-200 bg-gray-50/70 text-gray-600 font-semibold">
                                <th className="p-4 font-medium">Filename</th>
                                <th className="p-4 font-medium">Status</th>
                                <th className="p-4 font-medium text-right md:text-left">Chunks Created</th>
                                <th className="p-4 font-medium text-right">Uploaded Time</th>
                                <th className="p-4 font-medium text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 text-gray-700">
                            {documents.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="p-8 text-center text-gray-400 text-sm">
                                        No documents found in this workspace collection layer.
                                    </td>
                                </tr>
                            ) : (
                                documents.map((doc) => {
                                    const isDeleting = !!deletingIds[doc.id];
                                    return (
                                        <tr key={doc.id} className="hover:bg-gray-50/50 transition-colors">
                                            <td className="p-4 font-medium text-gray-900 max-w-xs md:max-w-md truncate">
                                                {doc.filename}
                                            </td>
                                            <td className="p-4">
                                                <span className={`px-2.5 py-1 rounded-md text-xs font-semibold border ${getStatusBadge(doc.status)}`}>
                                                    {doc.status}
                                                </span>
                                            </td>
                                            <td className="p-4 text-right md:text-left font-mono text-gray-600">
                                                {doc.chunks_created}
                                            </td>
                                            <td className="p-4 text-right text-gray-500 whitespace-nowrap text-xs">
                                                {new Date(doc.created_at).toLocaleString(undefined, {
                                                    dateStyle: "medium",
                                                    timeStyle: "short",
                                                })}
                                            </td>
                                            <td className="p-4 text-center">
                                                <button
                                                    onClick={() => handleDelete(doc.id, doc.filename)}
                                                    disabled={isDeleting}
                                                    className="text-xs font-semibold text-red-600 hover:text-red-800 disabled:text-gray-400 bg-red-50 hover:bg-red-100 disabled:bg-gray-50 px-2.5 py-1.5 rounded-md transition-all border border-red-100"
                                                >
                                                    {isDeleting ? "Wiping..." : "Delete"}
                                                </button>
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}