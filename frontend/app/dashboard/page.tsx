export default function DashboardPage() {
    return (
        <div className="space-y-6">
            <div className="border-b border-slate-900 pb-5">
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
                    Enterprise RAG Platform
                </h1>
                <p className="mt-1.5 text-sm text-slate-400">
                    Internal Knowledge Assistant and Vector Engine Control Hub
                </p>
            </div>

            {/* Grid Layout Metric Blocks */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 shadow-sm">
                    <div className="text-slate-500 font-mono text-[10px] uppercase font-bold tracking-wider mb-1">Vector Storage</div>
                    <div className="text-xl font-bold text-slate-100">ChromaDB Connected</div>
                </div>
                <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 shadow-sm">
                    <div className="text-slate-500 font-mono text-[10px] uppercase font-bold tracking-wider mb-1">Task Workers</div>
                    <div className="text-xl font-bold text-slate-100">Celery Pools Idle</div>
                </div>
                <div className="rounded-xl border border-slate-900 bg-slate-950 p-6 shadow-sm sm:col-span-2 lg:col-span-1">
                    <div className="text-slate-500 font-mono text-[10px] uppercase font-bold tracking-wider mb-1">Query Broker</div>
                    <div className="text-xl font-bold text-slate-100">FastAPI Operational</div>
                </div>
            </div>
        </div>
    );
}