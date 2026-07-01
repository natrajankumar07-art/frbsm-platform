/**
 * ExecutionTimeline — Reasoning timeline for SAM agent (Epic 4D).
 *
 * Displays the 7-stage execution timeline:
 * Intent → Planning → Tool Calls → Evidence → Reasoning → Report → Answer
 *
 * Never exposes chain-of-thought. Only high-level summaries per stage.
 */

export interface TimelineEvent {
  stage: string;
  label: string;
  detail: string;
  timestamp: string;
  status: "completed" | "running" | "pending" | "failed";
}

interface ExecutionTimelineProps {
  events: TimelineEvent[];
  planId?: string;
}

const STAGE_ICONS: Record<string, string> = {
  intent: "◎",
  planning: "⬡",
  tool_calls: "⚙",
  evidence_collection: "◈",
  reasoning: "◉",
  report_generation: "▤",
  final_answer: "✓",
};

const STATUS_CONNECTOR: Record<TimelineEvent["status"], string> = {
  completed: "bg-accent",
  running: "bg-blue-400 animate-pulse",
  pending: "bg-gray-300",
  failed: "bg-red-400",
};

const STATUS_ICON_BG: Record<TimelineEvent["status"], string> = {
  completed: "bg-accent text-white",
  running: "bg-blue-100 text-blue-600",
  pending: "bg-gray-100 text-gray-400",
  failed: "bg-red-100 text-red-600",
};

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return "";
  }
}

export function ExecutionTimeline({ events, planId }: ExecutionTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="px-4 py-6 text-center text-caption text-text-secondary">
        No execution timeline yet. Ask SAM a question to see reasoning steps.
      </div>
    );
  }

  return (
    <div className="px-3 py-2">
      {planId && (
        <p className="text-caption text-text-secondary mb-3 font-mono truncate">
          Plan {planId.slice(0, 8)}…
        </p>
      )}
      <ol className="relative">
        {events.map((event, idx) => {
          const isLast = idx === events.length - 1;
          const icon = STAGE_ICONS[event.stage] ?? "•";
          return (
            <li key={`${event.stage}-${idx}`} className="flex gap-3 mb-0">
              {/* Connector column */}
              <div className="flex flex-col items-center w-6 flex-shrink-0">
                <div
                  className={[
                    "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 z-10",
                    STATUS_ICON_BG[event.status],
                  ].join(" ")}
                >
                  {icon}
                </div>
                {!isLast && (
                  <div className={["w-0.5 flex-1 my-0.5 min-h-4", STATUS_CONNECTOR[event.status]].join(" ")} />
                )}
              </div>
              {/* Content */}
              <div className="flex-1 pb-3 min-w-0">
                <div className="flex items-baseline gap-2">
                  <span className="text-caption font-semibold text-text-primary">{event.label}</span>
                  {event.status === "running" && (
                    <span className="text-caption text-blue-500 animate-pulse">Running…</span>
                  )}
                  {event.status === "failed" && (
                    <span className="text-caption text-red-500">Failed</span>
                  )}
                </div>
                <p className="text-caption text-text-secondary mt-0.5 leading-relaxed break-words">
                  {event.detail}
                </p>
                {event.timestamp && (
                  <p className="text-caption text-text-secondary/60 mt-0.5">
                    {formatTime(event.timestamp)}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
