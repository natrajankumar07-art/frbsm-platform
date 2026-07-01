export interface ToolInfo {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
}

export interface ToolExecuteResponse {
  success: boolean;
  tool_name: string;
  data: Record<string, unknown>;
  evidence: ToolEvidence;
  markdown: string;
  error?: string | null;
}

export interface ToolEvidence {
  entity: string;
  snapshot_date: string;
  engines_used: string[];
  regulatory_refs: string[];
  source_tables: string[];
  confidence: "HIGH" | "MEDIUM" | "LOW";
}

export interface ReportTypeInfo {
  id: string;
  name: string;
  description: string;
}

export interface ReportResponse {
  report_type: string;
  title: string;
  entity: string;
  snapshot_date: string;
  generated_at: string;
  content_markdown: string;
  evidence: ToolEvidence;
  export_hints: Record<string, unknown>;
}

export interface WorkflowSseEvent {
  type: "tool_call" | "tool_result" | "token" | "done" | "error";
  tool?: string;
  params?: Record<string, unknown>;
  success?: boolean;
  markdown?: string;
  content?: string;
  evidence?: ToolEvidence;
  tool_calls_made?: Array<{ tool: string; success: boolean }>;
  session_id?: string;
}

export interface SessionMemory {
  session_id: string;
  active_entity_id: string | null;
  active_entity_name: string | null;
  active_snapshot_id: string | null;
  active_snapshot_date: string | null;
  recent_entity_ids: string[];
  recent_snapshot_ids: string[];
  report_history: Array<{ report_type: string; generated_at: string }>;
  last_tool_calls: Array<{ tool: string; summary: string; timestamp: string }>;
}

// ── Epic 4D — SAM Agent types ──────────────────────────────────────────────

export interface AgentSseEvent {
  type:
    | "intent_analyzed"
    | "plan_created"
    | "plan_start"
    | "step_start"
    | "step_complete"
    | "step_failed"
    | "step_skipped"
    | "plan_complete"
    | "timeline_ready"
    | "agent_done"
    | "error";
  // intent_analyzed
  intent?: string;
  domains?: string[];
  confidence?: number;
  // plan_created / plan_start
  plan_id?: string;
  total_steps?: number;
  tool_names?: string[];
  // step events
  step_id?: string;
  tool_name?: string;
  description?: string;
  duration_ms?: number;
  evidence?: ToolEvidence;
  error?: string;
  reason?: string;
  retry_count?: number;
  // plan_complete
  status?: string;
  steps_completed?: number;
  steps_failed?: number;
  steps_skipped?: number;
  // timeline_ready
  events?: AgentTimelineEvent[];
  execution_id?: string;
  // agent_done
  message?: string;
  timestamp?: string;
}

export interface AgentTimelineEvent {
  stage: string;
  label: string;
  detail: string;
  timestamp: string;
  status: "completed" | "running" | "pending" | "failed";
}

export interface AgentPlanStep {
  step_id: string;
  tool_name: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped" | "retrying";
  duration_ms?: number | null;
  retry_count?: number;
  error?: string | null;
  evidence?: Record<string, unknown> | null;
}

export interface AgentPlan {
  plan_id: string;
  intent: string;
  status: string;
  steps: AgentPlanStep[];
  steps_total: number;
  steps_completed: number;
  steps_failed: number;
  steps_skipped: number;
}
