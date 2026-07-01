/**
 * AgentProfile — SAM identity placeholder component (Epic 4D).
 *
 * Displays the agent's name, title, avatar, description, and status.
 * Epic 5 introduces the final SAM identity without changing this component's
 * contract — pass the real props and the design updates automatically.
 */

export type AgentStatus = "active" | "idle" | "thinking" | "error";

export interface AgentProfileProps {
  name?: string;
  title?: string;
  description?: string;
  status?: AgentStatus;
  compact?: boolean;
}

const STATUS_STYLES: Record<AgentStatus, string> = {
  active: "bg-green-500",
  idle: "bg-gray-400",
  thinking: "bg-blue-500 animate-pulse",
  error: "bg-red-500",
};

const STATUS_LABELS: Record<AgentStatus, string> = {
  active: "Active",
  idle: "Idle",
  thinking: "Thinking…",
  error: "Error",
};

export function AgentProfile({
  name = "SAM",
  title = "Supervisory AI Manager",
  description = "Intelligent banking teammate — explains regulatory position using validated engine outputs.",
  status = "idle",
  compact = false,
}: AgentProfileProps) {
  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {/* Placeholder avatar — Epic 5 replaces with final SAM avatar */}
        <div className="relative flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent font-bold text-sm select-none">
            S
          </div>
          <span
            className={[
              "absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white",
              STATUS_STYLES[status],
            ].join(" ")}
          />
        </div>
        <div className="min-w-0">
          <p className="text-body font-semibold text-text-primary leading-none">{name}</p>
          <p className="text-caption text-text-secondary truncate">{STATUS_LABELS[status]}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 p-3 bg-surface rounded-lg border border-border">
      {/* Placeholder avatar — Epic 5 replaces with final SAM avatar */}
      <div className="relative flex-shrink-0">
        <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center text-accent font-bold text-xl select-none">
          S
        </div>
        <span
          className={[
            "absolute bottom-0.5 right-0.5 w-3 h-3 rounded-full border-2 border-white",
            STATUS_STYLES[status],
          ].join(" ")}
        />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <h3 className="text-heading font-semibold text-text-primary">{name}</h3>
          <span className="text-caption text-text-secondary">{title}</span>
        </div>
        <p className="text-caption text-text-secondary mt-0.5 leading-relaxed">{description}</p>
        <div className="flex items-center gap-1.5 mt-1.5">
          <span className={["w-2 h-2 rounded-full", STATUS_STYLES[status]].join(" ")} />
          <span className="text-caption text-text-secondary">{STATUS_LABELS[status]}</span>
        </div>
      </div>
    </div>
  );
}
