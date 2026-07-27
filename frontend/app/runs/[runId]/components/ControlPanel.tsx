"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export function ControlPanel({ runId, status }: { runId: string; status: string }) {
  const [terminateReason, setTerminateReason] = useState("");
  const [showTerminate, setShowTerminate] = useState(false);

  const isActive = status === "active" || status === "sleeping";

  const handleTerminate = async () => {
    await api.terminateRun(runId, terminateReason || "Manual termination");
    setShowTerminate(false);
  };

  if (!isActive && status !== "sleeping") return null;

  return (
    <div className="flex items-center gap-2">
      {status === "active" && (
        <button onClick={() => api.interruptRun(runId)} className="btn-warning text-xs px-3 py-1.5">
          ⏸ Pause
        </button>
      )}
      {isActive && (
        <button onClick={() => setShowTerminate(true)} className="btn-danger text-xs px-3 py-1.5">
          ⏹ Terminate
        </button>
      )}

      {/* Terminate Modal */}
      {showTerminate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-96 shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Terminate Run</h3>
            <p className="text-sm text-slate-600 mb-4">
              This will permanently end the workflow for Order. This action cannot be undone.
            </p>
            <input
              type="text"
              value={terminateReason}
              onChange={(e) => setTerminateReason(e.target.value)}
              className="input-field mb-4"
              placeholder="Reason for termination..."
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowTerminate(false)} className="btn-secondary text-xs">
                Cancel
              </button>
              <button onClick={handleTerminate} className="btn-danger text-xs">
                Confirm Terminate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}