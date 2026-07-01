import { format, parseISO } from "date-fns";
import { clsx } from "clsx";

export type EventType =
  | "snapshot_processed"
  | "engines_executed"
  | "report_generated"
  | "alert_raised"
  | "ai_recommendation"
  | "workflow_execution";

export interface ExecutiveTimelineEvent {
  id: string;
  type: EventType;
  title: string;
  detail: string;
  timestamp: string;
}

interface ExecutiveDashTimelineProps {
  events: ExecutiveTimelineEvent[];
}

const EVENT_CONFIG: Record<
  EventType,
  { icon: string; dotColor: string; textColor: string }
> = {
  snapshot_processed: {
    icon: "◎",
    dotColor: "bg-accent dark:bg-blue-500",
    textColor: "text-accent dark:text-blue-400",
  },
  engines_executed: {
    icon: "⚙",
    dotColor: "bg-positive dark:bg-green-500",
    textColor: "text-positive dark:text-green-400",
  },
  report_generated: {
    icon: "▤",
    dotColor: "bg-violet-500 dark:bg-violet-400",
    textColor: "text-violet-600 dark:text-violet-400",
  },
  alert_raised: {
    icon: "⚠",
    dotColor: "bg-warning dark:bg-amber-500",
    textColor: "text-warning dark:text-amber-400",
  },
  ai_recommendation: {
    icon: "◉",
    dotColor: "bg-accent dark:bg-blue-500",
    textColor: "text-accent dark:text-blue-400",
  },
  workflow_execution: {
    icon: "⬡",
    dotColor: "bg-text-secondary dark:bg-gray-500",
    textColor: "text-text-secondary dark:text-gray-400",
  },
};

function formatTs(ts: string): string {
  try {
    return format(parseISO(ts), "dd MMM, HH:mm");
  } catch {
    return ts;
  }
}

export function ExecutiveDashTimeline({ events }: ExecutiveDashTimelineProps) {
  return (
    <div
      className="card dark:bg-gray-900 dark:border-gray-700 flex flex-col"
      data-testid="executive-dash-timeline"
    >
      <h3 className="text-body font-semibold text-text-primary dark:text-gray-100 mb-4">
        Executive Timeline
      </h3>
      {events.length === 0 ? (
        <p className="text-body text-text-secondary dark:text-gray-400 text-center py-6">
          No events yet.
        </p>
      ) : (
        <ol className="relative space-y-0">
          {events.map((ev, idx) => {
            const cfg = EVENT_CONFIG[ev.type];
            const isLast = idx === events.length - 1;
            return (
              <li key={ev.id} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div
                    className={clsx(
                      "h-5 w-5 rounded-full flex items-center justify-center text-white text-xs flex-shrink-0 z-10",
                      cfg.dotColor
                    )}
                  >
                    {cfg.icon}
                  </div>
                  {!isLast && (
                    <div className="w-px flex-1 bg-border dark:bg-gray-700 my-0.5 min-h-4" />
                  )}
                </div>
                <div className="pb-3 flex-1 min-w-0">
                  <p className={clsx("text-caption font-semibold", cfg.textColor)}>
                    {ev.title}
                  </p>
                  <p className="text-caption text-text-secondary dark:text-gray-400 leading-relaxed">
                    {ev.detail}
                  </p>
                  <p className="text-caption text-text-secondary/60 dark:text-gray-500 mt-0.5" style={{ fontSize: "10px" }}>
                    {formatTs(ev.timestamp)}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
