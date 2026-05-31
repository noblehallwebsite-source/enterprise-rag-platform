"use client";

import { useState } from "react";
import { api } from "@/services/api";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [taskId, setTaskId] = useState("");
    const [message, setMessage] = useState("");

    async function uploadFile() {
        if (!file) return;

        try {
            const formData = new FormData();

            formData.append(
                "tenant_id",
                "company-a"
            );

            formData.append(
                "file",
                file
            );

            const response = await api.post(
                "/upload",
                formData,
                {
                    headers: {
                        "Content-Type":
                            "multipart/form-data",
                    },
                }
            );

            setTaskId(response.data.task_id);

            setMessage(
                "Upload accepted."
            );

        } catch (error) {
            console.error(error);

            setMessage(
                "Upload failed."
            );
        }
    }

    return (
        <div className="max-w-xl">

            <h1 className="text-3xl font-bold mb-6">
                Upload Document
            </h1>

            <input
                type="file"
                onChange={(e) =>
                    setFile(
                        e.target.files?.[0] || null
                    )
                }
            />

            <button
                onClick={uploadFile}
                className="mt-4 px-4 py-2 bg-black text-white rounded"
            >
                Upload
            </button>

            {message && (
                <div className="mt-4">
                    {message}
                </div>
            )}

            {taskId && (
                <div className="mt-4">
                    Task ID:
                    <div className="font-mono">
                        {taskId}
                    </div>
                </div>
            )}
        </div>
    );
}