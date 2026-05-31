"use client";

import { useState } from "react";
import { api } from "@/services/api";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [taskId, setTaskId] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    async function uploadFile() {
        if (!file || loading) return;

        setLoading(true);
        setMessage("");

        try {
            const formData = new FormData();

            formData.append("tenant_id", "company-a");
            formData.append("file", file);

            const response = await api.post("/upload", formData);

            setTaskId(response.data.task_id);
            setMessage("Upload accepted. Processing started.");
        } catch (error) {
            console.error(error);
            setMessage("Upload failed.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="max-w-xl p-6">
            <h1 className="text-3xl font-bold mb-6">
                Upload Document
            </h1>

            <div className="space-y-4">
                <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) =>
                        setFile(e.target.files?.[0] || null)
                    }
                />

                <button
                    onClick={uploadFile}
                    disabled={!file || loading}
                    className="px-4 py-2 bg-black text-white rounded disabled:opacity-50"
                >
                    {loading ? "Uploading..." : "Upload"}
                </button>
            </div>

            {message && (
                <div className="mt-4 text-sm">
                    {message}
                </div>
            )}

            {taskId && (
                <div className="mt-4">
                    <div className="text-sm font-semibold">
                        Task ID:
                    </div>

                    <div className="font-mono bg-slate-100 p-2 rounded mt-1 break-all">
                        {taskId}
                    </div>
                </div>
            )}
        </div>
    );
}