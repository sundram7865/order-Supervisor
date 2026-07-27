// frontend/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON(url: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  // Supervisors
  listSupervisors: () => fetchJSON("/api/supervisors"),
  getSupervisor: (id: string) => fetchJSON(`/api/supervisors/${id}`),
  createSupervisor: (data: any) =>
    fetchJSON("/api/supervisors", { method: "POST", body: JSON.stringify(data) }),

  // Runs
  listRuns: (status?: string) =>
    fetchJSON(`/api/runs${status ? `?status=${status}` : ""}`),
  getRun: (id: string) => fetchJSON(`/api/runs/${id}`),
  startRun: (data: any) =>
    fetchJSON("/api/runs", { method: "POST", body: JSON.stringify(data) }),
  getRunTimeline: (id: string, kind?: string) =>
    fetchJSON(`/api/runs/${id}/timeline${kind ? `?kind=${kind}` : ""}`),

  // Events
  injectEvent: (runId: string, eventType: string, payload?: any) =>
    fetchJSON(`/api/runs/${runId}/events`, {
      method: "POST",
      body: JSON.stringify({ event_type: eventType, payload: payload || {} }),
    }),

  // Instructions
  addInstruction: (runId: string, instruction: string) =>
    fetchJSON(`/api/runs/${runId}/instructions`, {
      method: "POST",
      body: JSON.stringify({ instruction }),
    }),

  // Controls
  interruptRun: (runId: string) =>
    fetchJSON(`/api/runs/${runId}/interrupt`, { method: "POST" }),
  resumeRun: (runId: string) =>
    fetchJSON(`/api/runs/${runId}/resume`, { method: "POST" }),
  terminateRun: (runId: string, reason?: string) =>
    fetchJSON(`/api/runs/${runId}/terminate`, {
      method: "POST",
      body: JSON.stringify({ reason: reason || "Manual termination" }),
    }),
};