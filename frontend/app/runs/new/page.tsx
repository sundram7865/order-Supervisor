"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Supervisor } from "@/lib/types";
import { useRouter, useSearchParams } from "next/navigation";

export default function NewRun() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preSelectedSupervisor = searchParams.get("supervisor");

  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);
  const [supervisorId, setSupervisorId] = useState(preSelectedSupervisor || "");
  const [orderId, setOrderId] = useState("");
  const [contextJson, setContextJson] = useState(
    '{\n  "amount": 150.00,\n  "customer": "Alice Johnson",\n  "status": "processing"\n}'
  );
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.listSupervisors().then(setSupervisors);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const context = JSON.parse(contextJson);
      const run = await api.startRun({
        supervisor_id: supervisorId,
        order_id: orderId,
        order_context: context,
      });
      router.push(`/runs/${run.id}`);
    } catch (err) {
      alert("Invalid JSON in order context. Please check your syntax.");
      setSubmitting(false);
    }
  };

  const selectedSupervisor = supervisors.find((s) => s.id === supervisorId);

  return (
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Start New Run</h1>
        <p className="text-sm text-slate-500 mt-1">Launch an AI supervisor for a new order</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Supervisor Selection */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Supervisor Template</label>
            <select
              value={supervisorId}
              onChange={(e) => setSupervisorId(e.target.value)}
              className="select-field"
              required
            >
              <option value="">Select a supervisor template...</option>
              {supervisors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.wake_aggressiveness} aggressiveness)
                </option>
              ))}
            </select>
            {selectedSupervisor && (
              <div className="mt-3 p-3 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-500 mb-1">Instructions:</p>
                <p className="text-sm text-slate-700">{selectedSupervisor.base_instruction}</p>
                <div className="flex gap-1 mt-2">
                  {selectedSupervisor.available_actions.map((a) => (
                    <span key={a} className="text-xs px-1.5 py-0.5 bg-white text-slate-600 rounded border">
                      {a.replace("message_", "").replace("_", " ")}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Order ID */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Order ID</label>
            <input
              type="text"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              className="input-field"
              placeholder="e.g., ORD-2025-001"
              required
            />
          </div>
        </div>

        {/* Order Context */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Order Context (JSON)</label>
            <p className="text-xs text-slate-500 mb-2">
              Provide order details as JSON. This context is available to the agent during reasoning.
            </p>
            <textarea
              value={contextJson}
              onChange={(e) => setContextJson(e.target.value)}
              rows={8}
              className="input-field font-mono text-sm"
              spellCheck={false}
            />
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-3">
          <button type="submit" disabled={submitting} className="btn-primary">
            {submitting ? "Starting..." : "Start Run"}
          </button>
          <button type="button" onClick={() => router.back()} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}