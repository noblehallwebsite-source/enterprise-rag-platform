"use client";

import Link from "next/link";

export default function Sidebar() {
    return (
        <aside className="w-64 bg-black text-white min-h-screen">
            <div className="p-6 text-xl font-bold">
                Enterprise RAG
            </div>

            <nav className="px-4 space-y-2">

                <Link
                    href="/dashboard"
                    className="block p-3 rounded hover:bg-gray-800"
                >
                    Dashboard
                </Link>

                <Link
                    href="/dashboard/upload"
                    className="block p-3 rounded hover:bg-gray-800"
                >
                    Uploads
                </Link>

                <Link
                    href="/dashboard/documents"
                    className="block p-3 rounded hover:bg-gray-800"
                >
                    Documents
                </Link>

                <Link
                    href="/dashboard/search"
                    className="block p-3 rounded hover:bg-gray-800"
                >
                    Search
                </Link>

                <Link
                    href="/dashboard/chat"
                    className="block p-3 rounded hover:bg-gray-800"
                >
                    AI Chat
                </Link>

            </nav>
        </aside>
    );
}