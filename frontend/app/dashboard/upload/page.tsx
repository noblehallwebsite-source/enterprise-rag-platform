"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [taskId, setTaskId] = useState("");
    const [message, setMessage] = useState("");
    const [mounted, setMounted] = useState(false);

    // Eliminates compilation route hydration errors
    useEffect(() => {
        setMounted(true);
    }, []);

    async function uploadFile() {
        if (!file) return;

        try {
            setMessage("Uploading document securely...");
            const formData = new FormData();
            formData.append("tenant_id", "company-a");
            formData.append("file", file);

            // 🚀 Hits your clean Nginx relative endpoint path. 
            // No ports, no backend IPs, and no private API keys are ever leaked to browser bundles!
            const response = await axios.post("/api/upload", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            // Captures the Celery background processing task ID returned by FastAPI
            setTaskId(response.data.task_id);
            setMessage("Upload accepted. Processing pipeline started successfully.");
        } catch (error: any) {
            console.error("Upload Event Error:", error);
            setMessage("Secure upload transaction failed.");
        }
    }

    if (!mounted) {
        return <div className="max-w-xl p-6 font-sans">Initializing security infrastructure...</div>;
    }

    return (
        <div className="max-w-xl p-6 font-sans">
            <h1 className="text-3xl font-bold mb-6">Upload Document</h1>

            <div className="space-y-4">
                <input
                    type="file"
                    accept=".pdf"
                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-black hover:file:bg-slate-200"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />

                <button
                    onClick={uploadFile}
                    type="button"
                    className="mt-4 block px-4 py-2 bg-black text-white rounded font-medium transition-opacity hover:opacity-90"
                >
                    Upload Document
                </button>
            </div>

            {message && (
                <div className="mt-6 p-3 bg-slate-100 text-sm font-medium rounded">
                    {message}
                </div>
            )}

            {taskId && (
                <div className="mt-4 p-4 border border-slate-200 rounded">
                    <span className="text-sm text-slate-500 font-semibold">Background Task ID:</span>
                    <div className="font-mono bg-slate-50 p-2 text-xs rounded mt-2 break-all border border-slate-100">
                        {taskId}
                    </div>
                </div>
            )}
        </div>
    );
}