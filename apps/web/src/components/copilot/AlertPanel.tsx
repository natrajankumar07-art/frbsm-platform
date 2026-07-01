/**
 * AlertPanel — Autonomous monitoring alerts for SAM (Epic 4D).
 * Displays regulatory threshold breach alerts with severity colours.
 */

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, AlertCircle, Info, TrendingDown } from "lucide-react";

export interface MonitoringAlert {
  alert_id: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  category: string;
  title: string;
  message: string;
  entity: string;
  snapshot_date: string;
  metric_name?: string;
  metric_value?: number | null;
  threshold?: number | null;
  generated_at: string;
}

interface AlertsApiResponse {
  alerts: MonitoringAlert[];
  total: number;
  critical: number;
  high: number;
  medium: number;
}

const SEVERITY_STYLES: Record<MonitoringAlert["severity"], string> = {
  critical: "border-red-300 bg-red-50",
  high: "border-orange-300 bg-orange-50",
  medium: "border-yellow-300 bg-yellow-50",
  low: "border-blue-200 bg-blue-50",
  info: "border-gray-200 bg-gray-50",
};

const SEVERITY_TITLE: Record<MonitoringAlert["severity"], string> = {
  critical: "text-red-800",
  high: "text-orange-800",
  medium: "text-yellow-800",
  low: "text-blue-800",
  info: "text-gray-700",
};

const SEVERITY_BADGE: Record<MonitoringAlert["severity"], string> = {
  critical: "bg-red-100 text-red-700",
  high: "bg-orange-100 text-orange-700",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-blue-100 text-blue-700",
  info: "bg-gray-100 text-gray-600",
};

function SeverityIcon({ severity }: { severity: MonitoringAlert["severity"] }) {
  const cls = "h-3.5 w-3.5 flex-shrink-0";
  if (severity === "critical") return <AlertCircle className={`${cls} text-red-600`} />;
  if (severity === "high") return <AlertTriangle className={`${cls} text-orange-500`} />;
  if (severity === "medium") return <TrendingDown className={`${cls} text-yellow-600`} />;
  return <Info className={`${cls} text-blue-500`} />;
}

function AlertCard({ alert }: { alert: MonitoringAlert }) {
  return (
    <div className={["rounded-md border p-3 space-y-1", SEVERITY_STYLES[alert.severity]].join(" ")}>
      <div className="flex items-start gap-2">
        <SeverityIcon severity={alert.severity} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <p className={["text-caption font-semibold leading-tight", SEVERITY_TITLE[alert.severity]].join(" ")}>
              {alert.title}
            </p>
            <span className={["text-xs px-1.5 py-0.5 rounded font-medium", SEVERITY_BADGE[alert.severity]].join(" ")}>
              {alert.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-caption text-text-secondary mt-0.5 leading-relaxed">{alert.message}</p>
          {alert.metric_value != null && alert.threshold != null && (
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-text-secondary">
                Value: <strong>{alert.metric_value.toFixed(4)}</strong>
              </span>
              <span className="text-xs text-text-secondary">
                Min: <strong>{alert.threshold.toFixed(4)}</strong>
              </span>
            </div>
          )}
          <p className="text-caption text-text-secondary/70 mt-0.5">
            {alert.entity} · {alert.snapshot_date}
          </p>
        </div>
      </div>
    </div>
  );
}

async function fetchAlerts(): Promise<AlertsApiResponse> {
  const r = await fetch("/api/v1/copilot/agent/alerts");
  if (!r.ok) throw new Error("Failed to load alerts");
  return r.json() as Promise<AlertsApiResponse>;
}

export function AlertPanel() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["sam-alerts"],
    queryFn: fetchAlerts,
    staleTime: 60_000,
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="px-4 py-6 text-center text-caption text-text-secondary">
        Checking regulatory thresholds…
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 py-6 text-center text-caption text-red-500">
        Could not load alerts.{" "}
        <button onClick={() => void refetch()} className="underline">Retry</button>
      </div>
    );
  }

  const alerts = data?.alerts ?? [];

  if (alerts.length === 0) {
    return (
      <div className="px-4 py-6 text-center space-y-1">
        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mx-auto">
          <span className="text-green-600 text-sm font-bold">✓</span>
        </div>
        <p className="text-caption text-text-secondary">All metrics within thresholds</p>
      </div>
    );
  }

  return (
    <div className="px-3 py-2 space-y-2">
      {/* Summary row */}
      <div className="flex items-center justify-between">
        <span className="text-caption font-semibold text-text-primary">
          {alerts.length} Alert{alerts.length !== 1 ? "s" : ""}
        </span>
        <div className="flex gap-1.5">
          {(data?.critical ?? 0) > 0 && (
            <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded font-medium">
              {data?.critical} critical
            </span>
          )}
          {(data?.high ?? 0) > 0 && (
            <span className="text-xs bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded font-medium">
              {data?.high} high
            </span>
          )}
        </div>
      </div>
      {alerts.map((a) => <AlertCard key={a.alert_id} alert={a} />)}
    </div>
  );
}
