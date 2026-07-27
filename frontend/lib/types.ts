// frontend/lib/types.ts
export interface Supervisor {
  id: string;
  name: string;
  base_instruction: string;
  available_actions: string[];
  wake_aggressiveness: string;
  model_config: Record<string, any>;
  created_at: string;
}

export interface Run {
  id: string;
  supervisor_id: string;
  order_id: string;
  workflow_id: string;
  status: string;
  memory_summary: string;
  next_wake_at: string | null;
  order_context: Record<string, any>;
  extra_instructions: string[];
  final_summary: Record<string, any> | null;
  event_count: number;
  created_at: string;
  updated_at: string;
}

export interface ActivityLogEntry {
  id: string;
  run_id: string;
  kind: string;
  payload: Record<string, any>;
  importance: string;
  created_at: string;
}