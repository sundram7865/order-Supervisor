import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Order Supervisor | AI-Powered Order Management",
  description: "Long-running AI supervisor that oversees orders from creation to completion",
};

const navigation = [
  { name: "Dashboard", href: "/", icon: "◈" },
  { name: "Runs", href: "/runs", icon: "⊞" },
  { name: "New Supervisor", href: "/supervisors/new", icon: "+" },
  { name: "New Run", href: "/runs/new", icon: "→" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-60 bg-slate-900 text-white flex flex-col flex-shrink-0">
            <div className="px-5 py-6 border-b border-slate-700">
              <h1 className="text-lg font-bold tracking-tight">Order Supervisor</h1>
              <p className="text-xs text-slate-400 mt-1">AI-Powered POC</p>
            </div>
            <nav className="flex-1 px-3 py-4 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  <span className="w-5 text-center text-slate-400">{item.icon}</span>
                  {item.name}
                </Link>
              ))}
            </nav>
            <div className="px-5 py-4 border-t border-slate-700">
              <p className="text-xs text-slate-500">Temporal + FastAPI + Next.js</p>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-auto">
            <div className="max-w-7xl mx-auto px-6 py-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}