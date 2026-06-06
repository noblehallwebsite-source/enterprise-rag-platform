"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface SidebarProps {
    isOpen: boolean;
    setIsOpen: (open: boolean) => void;
}

export default function DashboardSidebar({ isOpen, setIsOpen }: SidebarProps) {
    const pathname = usePathname();

    const links = [
        { name: "Overview", href: "/dashboard", icon: "📊" },
        { name: "Documents", href: "/dashboard/documents", icon: "📂" },
        { name: "AI Chat", href: "/dashboard/chat", icon: "🧠" },
        { name: "Search", href: "/dashboard/search", icon: "🔍" },
        { name: "Settings", href: "/dashboard/settings", icon: "⚙️" },
    ];

    const SidebarContent = () => (
        <div className="flex h-full flex-col bg-slate-950 p-4 text-slate-200 border-r border-slate-900">
            <div className="flex h-14 items-center justify-between px-2 mb-6 border-b border-slate-900">
                <div className="flex items-center gap-2">
                    <span className="text-xl">⚡</span>
                    <h1 className="font-bold text-lg tracking-tight text-white">
                        Enterprise RAG
                    </h1>
                </div>
                {/* Mobile close interactive hit area trigger */}
                <button
                    onClick={() => setIsOpen(false)}
                    className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-800 text-slate-400 hover:text-white lg:hidden"
                >
                    ✕
                </button>
            </div>

            <nav className="flex-1 space-y-1">
                {links.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            onClick={() => setIsOpen(false)}
                            className={`flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-150 ${isActive
                                    ? "bg-slate-900 text-white border border-slate-800 shadow-inner"
                                    : "text-slate-400 hover:bg-slate-900/40 hover:text-slate-200 border border-transparent"
                                }`}
                        >
                            <span className="text-base opacity-80">{link.icon}</span>
                            {link.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="mt-auto border-t border-slate-900 pt-4 px-2">
                <div className="flex items-center gap-2.5 text-xs text-slate-500 font-mono bg-slate-900/20 p-2.5 rounded-lg border border-slate-900">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span>v1.0.0-prod-core</span>
                </div>
            </div>
        </div>
    );

    return (
        <>
            {/* DESKTOP BAR FIXED LOCK */}
            <aside className="hidden w-64 shrink-0 lg:block">
                <SidebarContent />
            </aside>

            {/* MOBILE SHEET DRAWER INTERFACE PANEL */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-50 flex bg-slate-950/80 backdrop-blur-xs lg:hidden"
                    onClick={() => setIsOpen(false)}
                >
                    <div
                        className="w-68 h-full shadow-2xl animate-in slide-in-from-left duration-200"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <SidebarContent />
                    </div>
                </div>
            )}
        </>
    );
}