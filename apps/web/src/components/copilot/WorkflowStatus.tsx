interface WorkflowStatusProps {
  events: WorkflowEvent[];
}

export interface WorkflowEvent {
  id: string;
  type: "tool_call" | "tool_result" | "thinking";
  tool?: string;
  success?: boolean;
  timestamp: string;
}

const TYPE_STYLES = {
  tool_call: "border-blue-200 bg-blue-50 text-blue-800",
  tool_result: "border-green-200 bg-green-50 text-green-800",
  thinking: "border-gray-200 bg-gray-50 text-gray-600",
};

const TYPE_ICON = {
  tool_call: "⚙",
  tool_result: "✓",
  thinking: "…",
};

export function WorkflowStatus({ events }: WorkflowStatusProps) {
  if (events.length === 0) return null;

  return (
    <div className="border border-border rounded-md mx-4 mb-2 overflow-hidden">
      <div className="px-3 py-1.5 bg-gray-50 border-b border-border">
        <span className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
          Workflow Progress
        </span>
      </div>
      <div className="p-2 space-y-1 max-h-32 overflow-y-auto">
        {events.map((event) => (
          <div
            key={event.id}
            className={[
              "flex items-center gap-2 text-xs px-2 py-1 rounded border",
              event.type === "tool_result" && event.success === false
                ? "border-red-200 bg-red-50 text-red-700"
                : TYPE_STYLES[event.type],
            ].join(" ")}
          >
            <span>{TYPE_ICON[event.type]}</span>
            <span className="font-mono">
              {event.tool ?? (event.type === "thinking" ? "AI is reasoning..." : "")}
            </span>
            <span className="ml-auto text-current opacity-60">{event.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
