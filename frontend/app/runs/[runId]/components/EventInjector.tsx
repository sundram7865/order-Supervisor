"use client";
import { useState } from "react";
import { api } from "@/lib/api";

const EVENT_TYPES = [
  { value: "payment_failed", label: "💳 Payment Failed", critical: true },
  { value: "payment_confirmed", label: "✅ Payment Confirmed", critical: false },
  { value: "shipment_delayed", label: "🚚 Shipment Delayed", critical: true },
  { value: "shipment_created", label: "📦 Shipment Created", critical: false },
  { value: "delivered", label: "🏠 Delivered", critical: true },
  { value: "refund_requested", label: "↩️ Refund Requested", critical: true },
  { value: "customer_message_received", label: "💬 Customer Message", critical: true },
  { value: "order_created", label: "🆕 Order Created", critical: false },
  { value: "no_update_for_n_hours", label: "⏰ No Update (N hours)", critical: false },
];

export function EventInjector({ runId }: { runId: string }) {
  const [eventType, setEventType] = useState(EVENT_TYPES[0].value);
  const [payload, setPayload] = useState("{}");
  const [sending, setSending] = useState(false);
  const [lastSent, setLastSent] = useState<string | null>(null);

  const inject = async () => {
    setSending(true);
    try {
      await api.injectEvent(runId, eventType, JSON.parse(payload));
      setLastSent(eventType);
      setPayload("{}");
    } catch (e) {
      alert("Invalid JSON payload");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-sm font-semibold text-slate-900">⚡ Inject Event</h2>
      </div>
      <div className="card-body space-y-3">
        <select
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
          className="select-field text-sm"
        >
          {EVENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label} {t.critical ? "(wakes agent)" : ""}
            </option>
          ))}
        </select>
        <textarea
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
          rows={2}
          className="input-field font-mono text-xs"
          placeholder='{"key": "value"}'
          spellCheck={false}
        />
        <button onClick={inject} disabled={sending} className="btn-primary w-full text-xs">
          {sending ? "Sending..." : "Send Event"}
        </button>
        {lastSent && (
          <p className="text-xs text-emerald-600">
            ✓ Last sent: {lastSent}
          </p>
        )}
      </div>
    </div>
  );
}