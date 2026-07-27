export function MemorySummary({ summary }: { summary: string }) {
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900">🧠 Memory Summary</h2>
        <span className="text-xs text-slate-400">
          {summary ? `${summary.length} chars` : "Empty"}
        </span>
      </div>
      <div className="card-body">
        {summary ? (
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50 rounded-lg p-4 border border-slate-100">
            {summary}
          </div>
        ) : (
          <div className="text-center py-6">
            <p className="text-sm text-slate-400">No memory yet</p>
            <p className="text-xs text-slate-400 mt-1">Waiting for first agent reasoning cycle...</p>
          </div>
        )}
      </div>
    </div>
  );
}