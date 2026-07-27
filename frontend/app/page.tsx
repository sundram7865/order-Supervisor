"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Supervisor, Run } from "@/lib/types";
import Link from "next/link";

export default function Dashboard() {
  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.listSupervisors(), api.listRuns()]).then(([sups, rns]) => {
      setSupervisors(sups);
      setRuns(rns);
      setLoading(false);
    });
  }, []);

  const activeRuns = runs.filter((r) => r.status === "active" || r.status === "sleeping");
  const completedRuns = runs.filter((r) => r.status === "completed" || r.status === "terminated");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Overview of your order supervision system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="stat-card">
          <div className="stat-icon bg-indigo-50 text-indigo-600">◈</div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{supervisors.length}</div>
            <div className="text-sm text-slate-500">Supervisor Templates</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon bg-emerald-50 text-emerald-600">⊞</div>
          <div>
            <div className="text-2xl font-bold text-emerald-600">{activeRuns.length}</div>
            <div className="text-sm text-slate-500">Active Runs</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon bg-slate-100 text-slate-600">✓</div>
          <div>
            <div className="text-2xl font-bold text-slate-600">{completedRuns.length}</div>
            <div className="text-sm text-slate-500">Completed Runs</div>
          </div>
        </div>
      </div>

      {/* Supervisors List */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">Supervisor Templates</h2>
          <Link href="/supervisors/new" className="btn-primary text-xs px-3 py-1.5">
            + New Supervisor
          </Link>
        </div>
        <div className="card-body">
          {supervisors.length === 0 ? (
            <p className="text-sm text-slate-500 text-center py-8">
              No supervisors yet. Create your first template to get started.
            </p>
          ) : (
            <div className="divide-y divide-slate-100">
              {supervisors.map((s) => (
                <div key={s.id} className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-900">{s.name}</span>
                      <span className={`badge text-xs ${
                        s.wake_aggressiveness === "high" ? "bg-red-50 text-red-700" :
                        s.wake_aggressiveness === "low" ? "bg-slate-100 text-slate-600" :
                        "bg-blue-50 text-blue-700"
                      }`}>
                        {s.wake_aggressiveness}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5 truncate">{s.base_instruction}</p>
                    <div className="flex gap-1 mt-1.5">
                      {s.available_actions.slice(0, 3).map((a) => (
                        <span key={a} className="text-xs px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded">
                          {a.replace("message_", "").replace("_", " ")}
                        </span>
                      ))}
                      {s.available_actions.length > 3 && (
                        <span className="text-xs text-slate-400">+{s.available_actions.length - 3} more</span>
                      )}
                    </div>
                  </div>
                  <Link
                    href={`/runs/new?supervisor=${s.id}`}
                    className="btn-primary text-xs px-3 py-1.5 ml-4 flex-shrink-0"
                  >
                    Start Run
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Runs */}
      {runs.length > 0 && (
        <div className="card mt-6">
          <div className="card-header flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-900">Recent Runs</h2>
            <Link href="/runs" className="text-sm text-indigo-600 hover:text-indigo-700">
              View all →
            </Link>
          </div>
          <div className="card-body">
            <div className="divide-y divide-slate-100">
              {runs.slice(0, 5).map((run) => (
                <Link
                  key={run.id}
                  href={`/runs/${run.id}`}
                  className="py-3 first:pt-0 last:pb-0 flex items-center justify-between hover:bg-slate-50 -mx-2 px-2 rounded transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-slate-900">Order {run.order_id}</span>
                    <span className={
                      run.status === "active" ? "badge-active" :
                      run.status === "sleeping" ? "badge-sleeping" :
                      run.status === "completed" ? "badge-completed" :
                      "badge-terminated"
                    }>
                      {run.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">
                    Events: {run.event_count} · {new Date(run.created_at).toLocaleDateString()}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}