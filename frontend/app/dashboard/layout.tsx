"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar"; // Adjust this import path if yours is different
import Header from "@/components/layout/Header";   // Adjust this import path if yours is different

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    // 📱 Initialize the display tracking toggle for responsive screen structures
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="min-h-screen bg-slate-950 flex">
            {/* 🚀 Fixed: Sidebar now receives its required parameters seamlessly */}
            <Sidebar isOpen={isOpen} setIsOpen={setIsOpen} />

            <div className="flex-1 flex flex-col min-w-0">
                {/* Pass state downstream to allow the header burger icon to control the menu toggle */}
                <Header onMenuToggle={() => setIsOpen((prev) => !prev)} />

                <main className="flex-1 p-6 md:p-8 overflow-y-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}