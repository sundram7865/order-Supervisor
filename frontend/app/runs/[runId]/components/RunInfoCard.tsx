"use client";
import { Run } from "@/lib/types";

export function RunInfoCard({ run }: { run: Run }) {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-base font-semibold text-slate-900">📊 Run Details</h2>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Order ID</p>
            <p className="text-sm font-medium text-slate-900 mt-0.5">{run.order_id}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Workflow ID</p>
            <p className="text-sm font-medium text-slate-900 mt-0.5 font-mono">{run.workflow_id?.slice(0, 12)}...</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Events</p>
            <p className="text-sm font-medium text-slate-900 mt-0.5">{run.event_count}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Next Wake</p>
            <p className="text-sm font-medium text-slate-900 mt-0.5">
              {run.next_wake_at
                ? new Date(run.next_wake_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Created</p>
            <p className="text-sm font-medium text-slate-900 mt-0.5">
              {new Date(run.created_at).toLocaleDateString()}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wider">Last Updated</p>
            <p className="text-sm font-medium text-slate-900 mt-0.5">
              {new Date(run.updated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-slate-500 uppercase tracking-wider">Order Context</p>
            <pre className="text-xs text-slate-600 mt-1 bg-slate-50 p-2 rounded-lg overflow-x-auto max-h-24">
              {JSON.stringify(run.order_context, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}