/**
 * AgentProfile — Official SAM identity component (Epic 4D.1).
 *
 * Displays:
 *   SAM
 *   Supervisory AI Manager
 *   Senior Banking Intelligence Advisor
 *   ● Online
 *
 * Sizes:
 *   compact — inline header chip (32px avatar)
 *   full    — card layout (64px desktop / 40px mobile)
 */

import { SamAvatar } from "./SamAvatar";

export type AgentStatus = "active" | "idle" | "thinking" | "error";

export interface AgentProfileProps {
  name?: string;
  title?: string;
  subtitle?: string;
  description?: string;
  status?: AgentStatus;
  compact?: boolean;
}

const STATUS_DOT: Record<AgentStatus, string> = {
  active:   "bg-green-500",
  idle:     "bg-green-500",    // always Online
  thinking: "bg-blue-400 animate-pulse",
  error:    "bg-red-500",
};

const STATUS_LABEL: Record<AgentStatus, string> = {
  active:   "Online",
  idle:     "Online",
  thinking: "Thinking…",
  error:    "Error",
};

export function AgentProfile({
  name     = "SAM",
  title    = "Supervisory AI Manager",
  subtitle = "Senior Banking Intelligence Advisor",
  status   = "idle",
  compact  = false,
}: AgentProfileProps) {

  /* ── Compact — header chip ─────────────────────────────────────────── */
  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <SamAvatar size="sm" statusDot />
        <div className="min-w-0">
          <p className="text-body font-semibold text-text-primary leading-none">{name}</p>
          <div className="flex items-center gap-1 mt-0.5">
            <span className={["w-1.5 h-1.5 rounded-full", STATUS_DOT[status]].join(" ")} />
            <p className="text-caption text-text-secondary">{STATUS_LABEL[status]}</p>
          </div>
        </div>
      </div>
    );
  }

  /* ── Full — card ───────────────────────────────────────────────────── */
  return (
    <div className="flex items-start gap-4 p-4 bg-surface rounded-xl border border-border shadow-sm">
      <SamAvatar size="lg" statusDot />
      <div className="min-w-0 flex-1">
        <h3 className="text-lg font-bold text-text-primary leading-tight">{name}</h3>
        <p className="text-body text-text-secondary font-medium">{title}</p>
        <p className="text-caption text-text-secondary/80 mt-0.5">{subtitle}</p>
        <div className="flex items-center gap-1.5 mt-2">
          <span className={["w-2 h-2 rounded-full", STATUS_DOT[status]].join(" ")} />
          <span className="text-caption font-medium text-text-secondary">
            {STATUS_LABEL[status]}
          </span>
        </div>
      </div>
    </div>
  );
}
