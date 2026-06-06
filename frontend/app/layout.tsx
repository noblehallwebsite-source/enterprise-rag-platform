"use client";

import { useState } from "react";
import DashboardSidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 font-sans text-slate-100 antialiased">

      {/* Shared Sidebar Component - Handles Desktop and Mobile Drawer states natively */}
      <DashboardSidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />

      {/* Main Panel Frame Content Stack */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onMenuToggle={() => setIsSidebarOpen(true)} />

        <main className="flex-1 overflow-auto bg-slate-900/40 p-4 md:p-8">
          <div className="mx-auto max-w-7xl h-full">
            {children}
          </div>
        </main>
      </div>

    </div>
  );
}