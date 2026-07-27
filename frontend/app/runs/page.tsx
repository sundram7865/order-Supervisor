"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Run } from "@/lib/types";
import Link from "next/link";

export default function RunsList() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRuns = () => {
      const statusParam = filter === "all" ? undefined : filter;
      api.listRuns(statusParam).then((data) => {
        setRuns(data);
        setLoading(false);
      });
    };
    fetchRuns();
    const interval = setInterval(fetchRuns, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const filters = [
    { value: "all", label: "All" },
    { value: "active", label: "Active" },
    { value: "sleeping", label: "Sleeping" },
    { value: "completed", label: "Completed" },
    { value: "terminated", label: "Terminated" },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active": return "badge-active";
      case "sleeping": return "badge-sleeping";
      case "completed": return "badge-completed";
      case "terminated": return "badge-terminated";
      default: return "badge";
    }
  };

  const getStatusDot = (status: string) => {
    switch (status) {
      case "active": return "bg-blue-500 animate-pulse";
      case "sleeping": return "bg-purple-400";
      case "completed": return "bg-emerald-500";
      case "terminated": return "bg-red-500";
      default: return "bg-slate-300";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Runs</h1>
          <p className="text-sm text-slate-500 mt-1">All order supervision workflows</p>
        </div>
        <Link href="/runs/new" className="btn-primary">
          + New Run
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {filters.map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-3.5 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              filter === f.value
                ? "bg-indigo-600 text-white"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Runs Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Order</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Events</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Memory</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Created</th>
                <th className="text-right px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-sm text-slate-500">
                    No runs found. Start a new run to begin monitoring orders.
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${getStatusDot(run.status)}`} />
                        <span className="text-sm font-medium text-slate-900">Order {run.order_id}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={getStatusBadge(run.status)}>{run.status}</span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-600">{run.event_count}</td>
                    <td className="px-5 py-3.5 text-sm text-slate-500 max-w-xs truncate">
                      {run.memory_summary || "—"}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">
                      {new Date(run.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/runs/${run.id}`}
                        className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}