/**
 * PlannerPanel — Shows SAM's active execution plan (Epic 4D).
 * Displays steps with status badges, tool names, and progress.
 */

import { SamAvatar } from "./SamAvatar";

export interface PlanStep {
  step_id: string;
  tool_name: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped" | "retrying";
  duration_ms?: number | null;
  retry_count?: number;
  error?: string | null;
}

export interface ActivePlan {
  plan_id: string;
  intent: string;
  steps: PlanStep[];
  steps_total: number;
  steps_completed: number;
  steps_failed: number;
  status: string;
}

interface PlannerPanelProps {
  plan: ActivePlan | null;
  isExecuting: boolean;
}

const STATUS_BADGE: Record<PlanStep["status"], string> = {
  pending: "bg-gray-100 text-gray-500",
  running: "bg-blue-100 text-blue-700 animate-pulse",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  skipped: "bg-yellow-100 text-yellow-700",
  retrying: "bg-orange-100 text-orange-700 animate-pulse",
};

const STATUS_DOT: Record<PlanStep["status"], string> = {
  pending: "bg-gray-300",
  running: "bg-blue-400 animate-pulse",
  completed: "bg-green-500",
  failed: "bg-red-500",
  skipped: "bg-yellow-400",
  retrying: "bg-orange-400 animate-pulse",
};

function formatDuration(ms: number | null | undefined): string {
  if (ms == null) return "";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function PlannerPanel({ plan, isExecuting }: PlannerPanelProps) {
  if (!plan) {
    return (
      <div className="px-4 py-6 text-center text-caption text-text-secondary">
        {isExecuting
          ? "Building execution plan…"
          : "No active plan. Ask SAM a question to see the execution plan."}
      </div>
    );
  }

  const progressPct =
    plan.steps_total > 0
      ? Math.round((plan.steps_completed / plan.steps_total) * 100)
      : 0;

  return (
    <div className="px-3 py-2 space-y-3">
      {/* SAM header */}
      <div className="flex items-center gap-2 pb-1 border-b border-border">
        <SamAvatar size="xs" statusDot />
        <span className="text-caption font-semibold text-text-primary">SAM — Execution Plan</span>
      </div>

      {/* Plan summary */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-caption font-semibold text-text-primary">Steps</span>
          <span className="text-caption text-text-secondary font-mono">
            {plan.steps_completed}/{plan.steps_total}
          </span>
        </div>
        {/* Progress bar */}
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className="h-full bg-accent transition-all duration-300 rounded-full"
            style={{ width: `${progressPct}%` }}
          />
        </div>
        <p className="text-caption text-text-secondary mt-1 truncate" title={plan.intent}>
          {plan.intent.length > 60 ? plan.intent.slice(0, 57) + "…" : plan.intent}
        </p>
      </div>

      {/* Steps list */}
      <ul className="space-y-1.5">
        {plan.steps.map((step, idx) => (
          <li
            key={step.step_id}
            className="flex items-start gap-2 p-2 rounded-md bg-white border border-border"
          >
            <div className="flex items-center gap-1.5 flex-shrink-0 mt-0.5">
              <span className="text-caption text-text-secondary w-3">{idx + 1}.</span>
              <span className={["w-2 h-2 rounded-full flex-shrink-0", STATUS_DOT[step.status]].join(" ")} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-caption font-mono text-text-primary truncate">
                  {step.tool_name}
                </span>
                <span className={["text-xs px-1.5 py-0.5 rounded font-medium", STATUS_BADGE[step.status]].join(" ")}>
                  {step.status}
                </span>
                {step.duration_ms != null && (
                  <span className="text-xs text-text-secondary">{formatDuration(step.duration_ms)}</span>
                )}
                {step.retry_count != null && step.retry_count > 0 && (
                  <span className="text-xs text-orange-600">↻ {step.retry_count}</span>
                )}
              </div>
              <p className="text-caption text-text-secondary truncate mt-0.5">{step.description}</p>
              {step.error && (
                <p className="text-xs text-red-600 mt-0.5 break-words">{step.error}</p>
              )}
            </div>
          </li>
        ))}
      </ul>

      {plan.steps_failed > 0 && (
        <p className="text-caption text-red-600">
          {plan.steps_failed} step{plan.steps_failed !== 1 ? "s" : ""} failed
        </p>
      )}
    </div>
  );
}
