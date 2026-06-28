import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { CheckCircle, XCircle } from "lucide-react";
import { api } from "../lib/api";
import { useEntity } from "../context/EntityContext";
import { MetricCard } from "../components/ui/MetricCard";
import { PageHeader } from "../components/ui/PageHeader";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { Badge } from "../components/ui/Badge";
import type { Scenario } from "../types/api";

export function Dashboard() {
  const { selected } = useEntity();

  const { data: snapshots, isLoading: loadingSnaps } = useQuery({
    queryKey: ["snapshots"],
    queryFn: () => api.snapshots.list({ size: 5 }),
  });

  const { data: scenarios, isLoading: loadingScenarios } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => api.scenarios.list({ size: 50 }),
  });

  const { data: positions, isLoading: loadingPositions } = useQuery({
    queryKey: ["positions-count"],
    queryFn: () => api.positions.list({ size: 1 }),
  });

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: () => api.health.ready(),
    refetchInterval: 30_000,
  });

  const isLoading = loadingSnaps || loadingScenarios || loadingPositions;
  if (isLoading) return <LoadingSpinner />;

  const latestSnapshot = snapshots?.items?.[0];
  const activeScenarios: Scenario[] = (scenarios?.items ?? []).filter(
    (s) => s.is_active
  );
  const regulatoryScenarios = activeScenarios.filter((s) => s.is_regulatory);

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle={
          selected
            ? `${selected.name} · ${selected.jurisdiction} · ${selected.regulator}`
            : "Select an entity from the top bar to view analytics"
        }
      />

      <div className="flex items-center gap-2 mb-6">
        {health?.status === "ok" ? (
          <>
            <CheckCircle className="h-4 w-4 text-positive" />
            <span className="text-caption text-positive">
              API connected · {health.service} {health.version}
            </span>
          </>
        ) : (
          <>
            <XCircle className="h-4 w-4 text-critical" />
            <span className="text-caption text-critical">API not reachable</span>
          </>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-4">
        <MetricCard
          label="Total Positions"
          value={positions?.meta?.total?.toLocaleString() ?? "—"}
          sub="Active positions in book"
        />
        <MetricCard
          label="Snapshots"
          value={snapshots?.meta?.total?.toLocaleString() ?? "—"}
          sub="Regulatory snapshots"
        />
        <MetricCard
          label="Active Scenarios"
          value={activeScenarios.length}
          sub={`${regulatoryScenarios.length} regulatory`}
        />
        <MetricCard
          label="Latest Snapshot"
          value={
            latestSnapshot
              ? format(new Date(latestSnapshot.reporting_date), "dd MMM yyyy")
              : "—"
          }
          sub={latestSnapshot?.status ?? "no snapshot"}
          status={latestSnapshot?.status === "locked" ? "positive" : "neutral"}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="text-heading font-semibold text-text-primary mb-4">
            Recent Snapshots
          </h2>
          {!snapshots?.items?.length ? (
            <p className="text-body text-text-secondary">No snapshots found.</p>
          ) : (
            <div className="space-y-3">
              {snapshots.items.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between py-2 border-b border-border last:border-0"
                >
                  <div>
                    <p className="text-body font-medium text-text-primary">
                      {format(new Date(s.reporting_date), "dd MMM yyyy")}
                    </p>
                    <p className="text-caption text-text-secondary">
                      {s.position_count.toLocaleString()} positions · {s.frozen_by}
                    </p>
                  </div>
                  <Badge
                    variant={
                      s.status === "locked"
                        ? "positive"
                        : s.status === "draft"
                        ? "warning"
                        : "default"
                    }
                  >
                    {s.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-heading font-semibold text-text-primary mb-4">
            Active Scenarios
          </h2>
          {activeScenarios.length === 0 ? (
            <p className="text-body text-text-secondary">No active scenarios.</p>
          ) : (
            <div className="space-y-3">
              {activeScenarios.slice(0, 6).map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between py-2 border-b border-border last:border-0"
                >
                  <div>
                    <p className="text-body font-medium text-text-primary">
                      {s.name}
                    </p>
                    <p className="text-caption text-text-secondary font-mono">
                      {s.code}
                    </p>
                  </div>
                  <div className="flex gap-1 flex-wrap justify-end">
                    {s.is_regulatory && (
                      <Badge variant="accent">Regulatory</Badge>
                    )}
                    {s.severity && (
                      <Badge
                        variant={
                          s.severity === "severe"
                            ? "critical"
                            : s.severity === "moderate"
                            ? "warning"
                            : "default"
                        }
                      >
                        {s.severity}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
