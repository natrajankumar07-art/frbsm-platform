import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Bell, CheckCircle2, Eye, AlertTriangle, Info, X } from "lucide-react";

interface AutonomousAlert {
  id: string;
  severity: "critical" | "warning" | "notice" | "info";
  title: string;
  message: string;
  category: string;
  metric_name: string | null;
  metric_value: number | null;
  recommendation: string | null;
  status: "open" | "acknowledged" | "resolved";
  created_at: string;
}

interface AlertsResponse {
  alerts: AutonomousAlert[];
  total: number;
  critical_count: number;
  warning_count: number;
  notice_count: number;
  info_count: number;
}

async function fetchAlerts(status?: string): Promise<AlertsResponse> {
  const q = status ? `?status=${status}` : "?status=open";
  const r = await fetch(`/api/v1/autonomous/alerts${q}`);
  if (!r.ok) return { alerts: [], total: 0, critical_count: 0, warning_count: 0, notice_count: 0, info_count: 0 };
  return r.json();
}

async function updateAlertStatus(id: string, status: string): Promise<void> {
  await fetch(`/api/v1/autonomous/alerts/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

function severityConfig(s: string) {
  switch (s) {
    case "critical":
      return { icon: X, label: "CRITICAL", bg: "bg-critical/10 border-critical/30", text: "text-critical", badge: "bg-critical" };
    case "warning":
      return { icon: AlertTriangle, label: "WARNING", bg: "bg-yellow-500/10 border-yellow-500/30", text: "text-yellow-500", badge: "bg-yellow-500" };
    case "notice":
      return { icon: Eye, label: "NOTICE", bg: "bg-accent/10 border-accent/30", text: "text-accent", badge: "bg-accent" };
    default:
      return { icon: Info, label: "INFO", bg: "bg-text-secondary/10 border-border", text: "text-text-secondary", badge: "bg-text-secondary" };
  }
}

export function AlertCenter() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<"open" | "acknowledged">("open");

  const { data, isLoading } = useQuery({
    queryKey: ["autonomous-alerts", filter],
    queryFn: () => fetchAlerts(filter),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => updateAlertStatus(id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["autonomous-alerts"] });
    },
  });

  const alerts = data?.alerts ?? [];

  return (
    <div className="rounded-xl border border-border bg-surface p-4 space-y-3" data-testid="alert-center">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-accent flex-shrink-0" />
          <span className="text-body font-semibold text-text-primary">Alert Center</span>
          {(data?.critical_count ?? 0) > 0 && (
            <span className="rounded-full bg-critical px-2 py-0.5 text-xs font-bold text-white">
              {data!.critical_count} CRITICAL
            </span>
          )}
        </div>
        <div className="flex gap-1">
          {(["open", "acknowledged"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={clsx(
                "rounded px-2 py-0.5 text-caption transition-colors capitalize",
                filter === f ? "bg-accent/20 text-accent font-medium" : "text-text-secondary hover:text-text-primary"
              )}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {isLoading && (
        <p className="text-body text-text-secondary py-4 text-center">Loading alerts…</p>
      )}

      {!isLoading && alerts.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-6">
          <CheckCircle2 className="h-8 w-8 text-green-500 opacity-60" />
          <p className="text-body text-text-secondary">No {filter} alerts</p>
        </div>
      )}

      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {alerts.map((alert) => {
          const cfg = severityConfig(alert.severity);
          const Icon = cfg.icon;
          return (
            <div
              key={alert.id}
              className={clsx(
                "rounded-lg border p-3 space-y-1 transition-opacity",
                cfg.bg,
                mutation.isPending ? "opacity-60" : ""
              )}
              data-testid={`alert-item-${alert.severity}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <Icon className={clsx("h-3.5 w-3.5 flex-shrink-0 mt-0.5", cfg.text)} />
                  <span className={clsx("text-caption font-bold flex-shrink-0", cfg.text)}>
                    {cfg.label}
                  </span>
                  <span className="text-caption font-medium text-text-primary truncate">
                    {alert.title}
                  </span>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  {alert.status === "open" && (
                    <button
                      onClick={() => mutation.mutate({ id: alert.id, status: "acknowledged" })}
                      className="text-caption text-text-secondary hover:text-accent px-1.5 py-0.5 rounded hover:bg-accent/10 transition-colors"
                      title="Acknowledge"
                    >
                      Ack
                    </button>
                  )}
                  {alert.status !== "resolved" && (
                    <button
                      onClick={() => mutation.mutate({ id: alert.id, status: "resolved" })}
                      className="text-caption text-text-secondary hover:text-green-500 px-1.5 py-0.5 rounded hover:bg-green-500/10 transition-colors"
                      title="Resolve"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
              <p className="text-caption text-text-secondary ml-5 line-clamp-2">
                {alert.message}
              </p>
              {alert.recommendation && (
                <p className="text-caption text-accent ml-5 italic line-clamp-1">
                  → {alert.recommendation}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
