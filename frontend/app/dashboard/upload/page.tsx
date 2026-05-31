"use client";

import { useState, useEffect } from "react";
import { api } from "@/services/api";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [taskId, setTaskId] = useState("");
    const [message, setMessage] = useState("");
    // Fix: Defer hydration checking to guarantee a clean client state
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    async function uploadFile() {
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append("tenant_id", "company-a");
            formData.append("file", file);

            const response = await api.post("/upload", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            setTaskId(response.data.task_id);
            setMessage("Upload accepted.");
        } catch (error) {
            console.error(error);
            setMessage("Upload failed.");
        }
    }

    // Prevent Next.js from evaluating server tracking IDs on pre-render
    if (!mounted) {
        return <div className="max-w-xl p-6">Loading component stack...</div>;
    }

    return (
        <div className="max-w-xl p-6">
            <h1 className="text-3xl font-bold mb-6">Upload Document</h1>

            {/* Explicitly omit the <form> wrapper completely to break Next.js server actions hooks */}
            <div className="space-y-4">
                <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />

                <button
                    onClick={uploadFile}
                    type="button"
                    className="mt-4 block px-4 py-2 bg-black text-white rounded"
                >
                    Upload
                </button>
            </div>

            {message && <div className="mt-4 text-sm font-medium">{message}</div>}

            {taskId && (
                <div className="mt-4">
                    Task ID:
                    <div className="font-mono bg-slate-100 p-2 rounded mt-1 break-all">
                        {taskId}
                    </div>
                </div>
            )}
        </div>
    );
}