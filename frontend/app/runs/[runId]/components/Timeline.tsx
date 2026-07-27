import { ActivityLogEntry } from "@/lib/types";

const kindConfig: Record<string, { icon: string; label: string; color: string; bgColor: string }> = {
  event: { icon: "📨", label: "Event", color: "border-l-blue-500", bgColor: "bg-blue-50" },
  action: { icon: "🔧", label: "Action", color: "border-l-emerald-500", bgColor: "bg-emerald-50" },
  reasoning: { icon: "🧠", label: "Reasoning", color: "border-l-purple-500", bgColor: "bg-purple-50" },
  instruction: { icon: "📝", label: "Instruction", color: "border-l-amber-500", bgColor: "bg-amber-50" },
  sleep_decision: { icon: "😴", label: "Sleep", color: "border-l-slate-400", bgColor: "bg-slate-50" },
  wake_decision: { icon: "⏰", label: "Wake", color: "border-l-orange-500", bgColor: "bg-orange-50" },
  final_output: { icon: "✅", label: "Final", color: "border-l-emerald-600", bgColor: "bg-emerald-50" },
  error: { icon: "❌", label: "Error", color: "border-l-red-500", bgColor: "bg-red-50" },
};

function formatPayload(kind: string, payload: Record<string, any>): string {
  switch (kind) {
    case "event":
      return payload.event_type || "Unknown event";
    case "action":
      return `${payload.action || "Unknown"}: ${payload.result || ""}`;
    case "reasoning":
      return payload.analysis?.reasoning?.substring(0, 200) || payload.reasoning?.substring(0, 200) || "Processing...";
    case "instruction":
      return payload.instruction || "";
    case "final_output":
      return payload.summary?.substring(0, 200) || "Final summary generated";
    case "sleep_decision":
      return payload.action || "Went to sleep";
    case "wake_decision":
      return `Reason: ${payload.reason || "Unknown"}`;
    default:
      return JSON.stringify(payload).substring(0, 100);
  }
}

export function Timeline({ activities }: { activities: ActivityLogEntry[] }) {
  if (!activities.length) {
    return (
      <div className="text-center py-8">
        <p className="text-sm text-slate-400">No activities yet</p>
        <p className="text-xs text-slate-400 mt-1">Events and agent actions will appear here</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {activities.map((a, index) => {
        const config = kindConfig[a.kind] || { icon: "•", label: a.kind, color: "border-l-slate-300", bgColor: "bg-slate-50" };
        const isLast = index === activities.length - 1;

        return (
          <div key={a.id} className="flex gap-3">
            {/* Timeline line + dot */}
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full ${config.bgColor} flex items-center justify-center text-sm border-2 border-white shadow-sm flex-shrink-0`}>
                {config.icon}
              </div>
              {!isLast && <div className="w-0.5 flex-1 bg-slate-200 my-1" />}
            </div>

            {/* Content */}
            <div className={`flex-1 pb-4 ${isLast ? "" : ""}`}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  {config.label}
                </span>
                {a.importance === "critical" && (
                  <span className="text-xs px-1.5 py-0.5 bg-red-50 text-red-600 rounded font-medium">
                    Critical
                  </span>
                )}
                <span className="text-xs text-slate-400">
                  {new Date(a.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                </span>
              </div>
              <div className="text-sm text-slate-700 leading-relaxed">
                {formatPayload(a.kind, a.payload)}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}