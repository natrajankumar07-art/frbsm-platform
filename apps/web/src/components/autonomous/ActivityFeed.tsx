import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Bell, FileText, Activity, ShieldAlert } from "lucide-react";
import { format } from "date-fns";

interface ActivityItem {
  id: string;
  type: string;
  title: string;
  detail: string;
  severity: string | null;
  timestamp: string;
}

interface ActivityResponse {
  items: ActivityItem[];
  total: number;
}

async function fetchActivity(): Promise<ActivityResponse> {
  const r = await fetch("/api/v1/autonomous/activity?limit=20");
  if (!r.ok) return { items: [], total: 0 };
  return r.json();
}

function itemConfig(type: string, severity: string | null) {
  switch (type) {
    case "alert_raised":
      return {
        Icon: Bell,
        dot: severity === "critical" ? "bg-critical" : severity === "warning" ? "bg-yellow-500" : "bg-accent",
      };
    case "briefing_generated":
      return { Icon: FileText, dot: "bg-green-500" };
    case "monitoring_run":
      return { Icon: Activity, dot: "bg-text-secondary" };
    default:
      return { Icon: ShieldAlert, dot: "bg-accent" };
  }
}

export function ActivityFeed() {
  const { data, isLoading } = useQuery({
    queryKey: ["autonomous-activity"],
    queryFn: fetchActivity,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  const items = data?.items ?? [];

  return (
    <div className="rounded-xl border border-border bg-surface p-4 space-y-3" data-testid="activity-feed">
      <div className="flex items-center gap-2">
        <Activity className="h-4 w-4 text-accent flex-shrink-0" />
        <span className="text-body font-semibold text-text-primary">Autonomous Activity</span>
      </div>

      {isLoading && (
        <p className="text-body text-text-secondary py-4 text-center">Loading activity…</p>
      )}

      {!isLoading && items.length === 0 && (
        <p className="text-body text-text-secondary py-4 text-center">No recent activity</p>
      )}

      <div className="relative max-h-80 overflow-y-auto pr-1">
        {/* Vertical line */}
        {items.length > 0 && (
          <div className="absolute left-2 top-0 bottom-0 w-px bg-border" />
        )}
        <div className="space-y-3 pl-6">
          {items.map((item) => {
            const { Icon, dot } = itemConfig(item.type, item.severity);
            return (
              <div key={item.id} className="relative" data-testid="activity-item">
                <div className={clsx("absolute -left-[22px] top-1 h-2.5 w-2.5 rounded-full border-2 border-surface", dot)} />
                <div className="space-y-0.5">
                  <div className="flex items-center gap-1.5">
                    <Icon className="h-3 w-3 text-text-secondary flex-shrink-0" />
                    <span className="text-caption font-medium text-text-primary">{item.title}</span>
                  </div>
                  <p className="text-caption text-text-secondary line-clamp-2">{item.detail}</p>
                  <p className="text-caption text-text-secondary/60">
                    {format(new Date(item.timestamp), "dd MMM HH:mm")}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
