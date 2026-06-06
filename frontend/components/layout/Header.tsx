"use client";

interface HeaderProps {
    onMenuToggle: () => void;
}

export default function Header({ onMenuToggle }: HeaderProps) {
    return (
        <header className="h-16 border-b border-slate-900 bg-slate-950 px-4 md:px-6 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
                <button
                    onClick={onMenuToggle}
                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 text-slate-400 hover:bg-slate-900 hover:text-slate-200 lg:hidden transition-colors"
                    aria-label="Toggle Navigation Sidebar"
                >
                    ☰
                </button>
                <h2 className="font-semibold text-sm md:text-base text-slate-200 tracking-tight">
                    Knowledge Platform Control Center
                </h2>
            </div>

            <div className="flex items-center gap-2.5">
                <div className="rounded-full border border-slate-800/80 bg-slate-900 px-3 py-1 font-mono text-xs font-semibold text-slate-400 shadow-inner">
                    tenant: <span className="text-slate-200">company-a</span>
                </div>
            </div>
        </header>
    );
}