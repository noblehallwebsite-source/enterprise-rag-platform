// frontend/src/app/dashboard/documents/page.tsx
"use client";

import { useEffect, useState } from "react";
import { Document } from "@/types/document";
import { getDocuments, deleteDocument, getDocumentDetails } from "@/services/documents";
import { DocumentDetailsPayload } from "@/types/document";

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [deletingIds, setDeletingIds] = useState<Record<string, boolean>>({});

    // Observability Layer States
    const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
    const [details, setDetails] = useState<DocumentDetailsPayload | null>(null);
    const [loadingDetails, setLoadingDetails] = useState(false);

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

    useEffect(() => {
        loadDocuments();
        const interval = setInterval(loadDocuments, 5000);
        return () => clearInterval(interval);
    }, []);

    // Handles fetching detailed telemetry and chunk blocks
    async function handleViewDetails(documentId: string) {
        try {
            setSelectedDocId(documentId);
            setLoadingDetails(true);
            setDetails(null); // Clear out old panel data instantly
            const detailedData = await getDocumentDetails(documentId);
            setDetails(detailedData);
        } catch (error) {
            console.error("Observability extraction breakdown failed:", error);
            alert("Could not extract vector fragments for this asset.");
            setSelectedDocId(null);
        } finally {
            setLoadingDetails(false);
        }
    }

    async function handleDelete(documentId: string, filename: string, e: React.MouseEvent) {
        e.stopPropagation(); // Prevents opening details when intent was to delete
        if (!confirm(`Are you sure you want to permanently drop "${filename}" and all associated vector chunks from ChromaDB?`)) {
            return;
        }

        try {
            setDeletingIds(prev => ({ ...prev, [documentId]: true }));
            await deleteDocument(documentId);
            setDocuments(prev => prev.filter(doc => doc.id !== documentId));
            if (selectedDocId === documentId) setSelectedDocId(null); // Close panel if open
        } catch (error) {
            console.error("Deletion lifecycle failure:", error);
            alert("Critical Error: Failed to cleanly evict document fragments.");
        } finally {
            setDeletingIds(prev => {
                const updated = { ...prev };
                delete updated[documentId];
                return updated;
            });
        }
    }

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "COMPLETED": return "bg-green-50 border-green-200 text-green-700";
            case "PROCESSING": return "bg-amber-50 border-amber-200 text-amber-700 animate-pulse";
            case "FAILED": return "bg-red-50 border-red-200 text-red-700";
            default: return "bg-gray-50 border-gray-200 text-gray-700";
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
        <div className="p-6 max-w-7xl mx-auto flex gap-6 relative">

            {/* Main Documents Workspace Table */}
            <div className="flex-1 transition-all duration-300">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Documents Engine</h1>
                        <p className="text-sm text-gray-500 mt-1">
                            Real-time multi-tenant data ingestion tracking and chunk metrics. Click a document to inspect fragments.
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
                                        const isSelected = selectedDocId === doc.id;
                                        return (
                                            <tr
                                                key={doc.id}
                                                onClick={() => handleViewDetails(doc.id)}
                                                className={`cursor-pointer transition-colors ${isSelected ? 'bg-blue-50/60 hover:bg-blue-50' : 'hover:bg-gray-50/50'}`}
                                            >
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
                                                    {new Date(doc.created_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}
                                                </td>
                                                <td className="p-4 text-center">
                                                    <button
                                                        onClick={(e) => handleDelete(doc.id, doc.filename, e)}
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

            {/* Observability Panel Side Drawer */}
            {selectedDocId && (
                <div className="w-[450px] bg-gray-50 border border-gray-200 rounded-xl shadow-xl p-5 flex flex-col h-[calc(100vh-100px)] sticky top-6 animate-in slide-in-from-right duration-200">
                    <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                        <h2 className="font-bold text-gray-900 text-lg">Document Details</h2>
                        <button
                            onClick={() => setSelectedDocId(null)}
                            className="text-gray-400 hover:text-gray-600 font-medium text-sm px-2 py-1 bg-white border rounded-md shadow-sm"
                        >
                            ✕ Close
                        </button>
                    </div>

                    {loadingDetails && (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-400 text-xs gap-2">
                            <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                            Streaming vector chunks from ChromaDB...
                        </div>
                    )}

                    {details && (
                        <div className="flex-1 overflow-y-auto mt-4 space-y-4 pr-1 text-xs">
                            {/* Metadata Overview Block */}
                            <div className="bg-white p-3.5 border border-gray-200 rounded-lg space-y-2">
                                <div className="text-gray-500 font-medium tracking-tight uppercase text-[10px]">Telemetry Card</div>
                                <div className="text-sm font-semibold text-gray-900 truncate">{details.document.filename}</div>
                                <div className="grid grid-cols-2 gap-2 pt-1 font-medium text-gray-600">
                                    <div>Status: <span className="font-semibold text-gray-800">{details.document.status}</span></div>
                                    <div>Total Chunks: <span className="font-semibold text-gray-800 font-mono">{details.document.chunks_created}</span></div>
                                </div>
                            </div>

                            {/* Unpacked Chunks Stack Loop */}
                            <div className="space-y-3">
                                <div className="text-gray-500 font-medium tracking-tight uppercase text-[10px] pl-1">Vector Spaces Chunk Registry</div>
                                {details.chunks.length === 0 ? (
                                    <div className="p-4 text-center bg-white border rounded-lg text-gray-400 italic">
                                        No text chunks extracted yet or zero vectors found for this indexing job.
                                    </div>
                                ) : (
                                    details.chunks.map((chunk, index) => (
                                        <div key={index} className="bg-white border border-gray-200 rounded-lg p-3.5 space-y-2 hover:shadow-sm transition-shadow">
                                            <div className="flex items-center justify-between border-b border-gray-100 pb-1.5 text-[11px]">
                                                <span className="font-bold text-blue-600 font-mono">Chunk #{chunk.metadata.chunk_index ?? index}</span>
                                                <span className="text-gray-400 scale-90 font-mono">len: {chunk.text.length}</span>
                                            </div>
                                            <p className="text-gray-700 leading-relaxed font-normal whitespace-pre-wrap font-sans text-xs bg-gray-50/50 p-2 rounded border border-gray-50">
                                                {chunk.text}
                                            </p>
                                            {Object.keys(chunk.metadata).length > 2 && (
                                                <div className="pt-1 flex flex-wrap gap-1 items-center">
                                                    <span className="text-[10px] text-gray-400 mr-1">Source context:</span>
                                                    {chunk.metadata.source && <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded text-[10px] font-mono">{String(chunk.metadata.source)}</span>}
                                                    {chunk.metadata.environment && <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded text-[10px] font-mono">{String(chunk.metadata.environment)}</span>}
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}