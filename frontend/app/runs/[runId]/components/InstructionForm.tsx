"use client";
import { useState } from "react";
import { api } from "@/lib/api";

const QUICK_INSTRUCTIONS = [
  "Prioritize speed over cost",
  "If shipment is delayed, escalate immediately",
  "Do not contact the customer without human review",
];

export function InstructionForm({ runId }: { runId: string }) {
  const [instruction, setInstruction] = useState("");
  const [adding, setAdding] = useState(false);

  const addInstruction = async (text?: string) => {
    const ins = text || instruction;
    if (!ins.trim()) return;
    setAdding(true);
    try {
      await api.addInstruction(runId, ins);
      setInstruction("");
    } catch (err) {
      alert("Failed to add instruction");
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-sm font-semibold text-slate-900">📝 Add Instruction</h2>
      </div>
      <div className="card-body space-y-3">
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          rows={2}
          className="input-field text-sm"
          placeholder="e.g., Prioritize speed over cost..."
        />
        <button
          onClick={() => addInstruction()}
          disabled={adding || !instruction.trim()}
          className="btn-secondary w-full text-xs"
        >
          {adding ? "Adding..." : "Add Instruction"}
        </button>

        <div className="border-t border-slate-100 pt-3">
          <p className="text-xs text-slate-500 mb-2">Quick add:</p>
          <div className="space-y-1.5">
            {QUICK_INSTRUCTIONS.map((qi) => (
              <button
                key={qi}
                onClick={() => addInstruction(qi)}
                className="w-full text-left text-xs text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 px-2 py-1.5 rounded transition-colors"
              >
                + {qi}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}