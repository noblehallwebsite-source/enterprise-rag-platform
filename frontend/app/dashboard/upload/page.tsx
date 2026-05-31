"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [taskId, setTaskId] = useState("");
    const [message, setMessage] = useState("");
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    async function uploadFile() {
        if (!file) {
            setMessage("Please select a valid PDF file first.");
            return;
        }

        try {
            setMessage("Uploading document securely...");
            setTaskId("");

            const formData = new FormData();
            formData.append("tenant_id", "company-a");
            formData.append("file", file);

            // 🛡️ The browser sends a clean request to Next.js.
            // Next.js middleware catches it on the server and attaches the secret key.
            const response = await axios.post("/api/upload", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            if (response.data && response.data.task_id) {
                setTaskId(response.data.task_id);
                setMessage("Upload accepted. Processing pipeline started successfully.");
            } else {
                setMessage("Upload succeeded, but no background task ID was returned.");
            }

        } catch (error: any) {
            console.error("Upload Event Error:", error);
            if (error.response && error.response.status === 422) {
                setMessage("Secure upload transaction failed: 422 Payload Unprocessable. Check validation keys/headers.");
            } else if (error.response && error.response.status === 403) {
                setMessage("Secure upload transaction failed: 403 Forbidden. Your API Key does not match the tenant ID.");
            } else {
                setMessage("Secure upload transaction failed. Check browser terminal console logs.");
            }
        }
    }

    if (!mounted) {
        return (
            <div className="max-w-xl p-6 font-sans">
                <div className="animate-pulse text-slate-500 font-medium">
                    Initializing security infrastructure...
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-xl p-6 font-sans">
            <h1 className="text-3xl font-bold mb-2 tracking-tight text-slate-900">Upload Document</h1>
            <p className="text-sm text-slate-500 mb-6">
                Upload raw enterprise artifacts (.pdf) directly to your secure RAG knowledge vault.
            </p>

            <div className="space-y-4 p-6 bg-slate-50 border border-slate-200 rounded-lg shadow-sm">
                <label className="block text-sm font-semibold text-slate-700">Select Document Location</label>
                <input
                    type="file"
                    accept=".pdf"
                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-slate-900 file:text-white hover:file:opacity-90 cursor-pointer"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />

                <button
                    onClick={uploadFile}
                    type="button"
                    className="mt-2 w-full px-4 py-2.5 bg-black text-white rounded-md font-medium text-sm shadow hover:bg-slate-800 transition-colors"
                >
                    Upload and Ingest
                </button>
            </div>

            {message && (
                <div className="mt-6 p-4 bg-slate-100 text-sm font-medium text-slate-800 rounded-lg border border-slate-200 break-words">
                    {message}
                </div>
            )}

            {taskId && (
                <div className="mt-4 p-4 bg-white border border-slate-200 rounded-lg shadow-sm">
                    <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1">
                        Asynchronous Pipeline Token (Celery Task ID)
                    </span>
                    <div className="font-mono bg-slate-50 p-2.5 text-xs text-emerald-700 rounded border border-slate-100 break-all select-all">
                        {taskId}
                    </div>
                </div>
            )}
        </div>
    );
}