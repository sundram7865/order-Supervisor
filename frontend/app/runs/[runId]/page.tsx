"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Run, ActivityLogEntry } from "@/lib/types";
import { Timeline } from "./components/Timeline";
import { EventInjector } from "./components/EventInjector";
import { InstructionForm } from "./components/InstructionForm";
import { ControlPanel } from "./components/ControlPanel";
import { MemorySummary } from "./components/MemorySummary";
import { RunInfoCard } from "./components/RunInfoCard";

export default function RunDetail() {
  const params = useParams();
  const runId = params.runId as string;
  const [run, setRun] = useState<Run | null>(null);
  const [timeline, setTimeline] = useState<ActivityLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [runData, timelineData] = await Promise.all([
          api.getRun(runId),
          api.getRunTimeline(runId),
        ]);
        setRun(runData);
        setTimeline(timelineData.activities);
      } catch (err) {
        console.error("Failed to fetch run data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [runId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!run) {
    return (
      <div className="card p-12 text-center">
        <p className="text-slate-500">Run not found</p>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active": return "badge-active";
      case "sleeping": return "badge-sleeping";
      case "completed": return "badge-completed";
      case "terminated": return "badge-terminated";
      default: return "badge";
    }
  };

  const isTerminal = run.status === "completed" || run.status === "terminated";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Order {run.order_id}</h1>
          <div className="flex items-center gap-3 mt-1">
            <span className={getStatusBadge(run.status)}>{run.status}</span>
            <span className="text-xs text-slate-400">Run ID: {run.id.slice(0, 8)}...</span>
            <span className="text-xs text-slate-400">{run.event_count} events processed</span>
          </div>
        </div>
        {!isTerminal && <ControlPanel runId={runId} status={run.status} />}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Run Info Card */}
          <RunInfoCard run={run} />

          {/* Memory Summary */}
          <MemorySummary summary={run.memory_summary} />

          {/* Final Summary */}
          {run.final_summary && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-base font-semibold text-slate-900">📋 Final Summary</h2>
              </div>
              <div className="card-body space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-1">Summary</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{run.final_summary.summary || "N/A"}</p>
                </div>
                {run.final_summary.important_actions?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-700 mb-2">Important Actions</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {run.final_summary.important_actions.map((a: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 bg-emerald-50 text-emerald-700 rounded-md">
                          {a}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {run.final_summary.key_learnings?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-700 mb-2">Key Learnings</h3>
                    <ul className="space-y-1">
                      {run.final_summary.key_learnings.map((l: string, i: number) => (
                        <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                          <span className="text-amber-500 mt-1">•</span>
                          {l}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {run.final_summary.feedback && (
                  <div>
                    <h3 className="text-sm font-semibold text-slate-700 mb-1">Feedback</h3>
                    <p className="text-sm text-slate-600 italic">{run.final_summary.feedback}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-base font-semibold text-slate-900">📜 Activity Timeline</h2>
            </div>
            <div className="card-body">
              <Timeline activities={timeline} />
            </div>
          </div>
        </div>

        {/* Right Column - Actions */}
        <div className="space-y-4">
          {!isTerminal && (
            <>
              <EventInjector runId={runId} />
              <InstructionForm runId={runId} />
            </>
          )}

          {/* Extra Instructions History */}
          {run.extra_instructions?.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2 className="text-sm font-semibold text-slate-900">📝 Extra Instructions</h2>
              </div>
              <div className="card-body">
                <div className="space-y-2">
                  {run.extra_instructions.map((ins, i) => (
                    <div key={i} className="text-xs text-slate-600 p-2 bg-amber-50 rounded-lg border border-amber-100">
                      {ins}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}