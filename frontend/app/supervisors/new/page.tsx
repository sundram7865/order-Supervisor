"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

const ALL_ACTIONS = [
  { value: "message_fulfillment_team", label: "Message Fulfillment Team", icon: "📦" },
  { value: "message_payments_team", label: "Message Payments Team", icon: "💳" },
  { value: "message_logistics_team", label: "Message Logistics Team", icon: "🚚" },
  { value: "message_customer", label: "Message Customer", icon: "📧" },
  { value: "create_internal_note", label: "Create Internal Note", icon: "📝" },
];

const AGGRESSIVENESS_OPTIONS = [
  { value: "low", label: "Low", desc: "Wake only on critical events (payment_failed, refund_requested)" },
  { value: "normal", label: "Normal", desc: "Balanced - wake on important business events" },
  { value: "high", label: "High", desc: "Wake on most events, proactive monitoring" },
];

export default function NewSupervisor() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [instruction, setInstruction] = useState("");
  const [selectedActions, setSelectedActions] = useState<string[]>(ALL_ACTIONS.map((a) => a.value));
  const [aggressiveness, setAggressiveness] = useState("normal");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createSupervisor({
        name,
        base_instruction: instruction,
        available_actions: selectedActions,
        wake_aggressiveness: aggressiveness,
      });
      router.push("/");
    } catch (err) {
      alert("Failed to create supervisor");
    } finally {
      setSubmitting(false);
    }
  };

  const toggleAction = (action: string) => {
    setSelectedActions((prev) =>
      prev.includes(action) ? prev.filter((a) => a !== action) : [...prev, action]
    );
  };

  return (
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Create Supervisor</h1>
        <p className="text-sm text-slate-500 mt-1">Configure an AI supervisor template for order monitoring</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Supervisor Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input-field"
              placeholder="e.g., OrderGuard Pro, Standard Monitor"
              required
            />
          </div>
        </div>

        {/* Base Instruction */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Base Instructions</label>
            <p className="text-xs text-slate-500 mb-2">
              These instructions guide the AI's decision-making for every order it supervises.
            </p>
            <textarea
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              rows={4}
              className="input-field"
              placeholder="You are an order supervisor. Monitor orders from creation to delivery. Alert on payment failures and shipping delays. Keep customers informed of any issues..."
              required
            />
          </div>
        </div>

        {/* Available Actions */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Available Actions</label>
            <p className="text-xs text-slate-500 mb-3">
              Select which tools the agent can use. All actions are logged for review.
            </p>
            <div className="grid grid-cols-1 gap-2">
              {ALL_ACTIONS.map((action) => (
                <label
                  key={action.value}
                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedActions.includes(action.value)
                      ? "border-indigo-300 bg-indigo-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedActions.includes(action.value)}
                    onChange={() => toggleAction(action.value)}
                    className="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                  />
                  <span className="text-lg">{action.icon}</span>
                  <span className="text-sm font-medium text-slate-900">{action.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Aggressiveness */}
        <div className="card">
          <div className="card-body">
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Wake Aggressiveness</label>
            <p className="text-xs text-slate-500 mb-3">
              Controls how often the agent wakes up to check on orders.
            </p>
            <div className="grid grid-cols-1 gap-2">
              {AGGRESSIVENESS_OPTIONS.map((opt) => (
                <label
                  key={opt.value}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                    aggressiveness === opt.value
                      ? "border-indigo-300 bg-indigo-50"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="aggressiveness"
                    value={opt.value}
                    checked={aggressiveness === opt.value}
                    onChange={(e) => setAggressiveness(e.target.value)}
                    className="w-4 h-4 text-indigo-600 mt-0.5 focus:ring-indigo-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-900">{opt.label}</span>
                    <p className="text-xs text-slate-500 mt-0.5">{opt.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-3">
          <button type="submit" disabled={submitting} className="btn-primary">
            {submitting ? "Creating..." : "Create Supervisor"}
          </button>
          <button type="button" onClick={() => router.back()} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}