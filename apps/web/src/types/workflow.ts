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
