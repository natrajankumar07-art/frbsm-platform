import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { api } from "../../lib/api";
import { PageHeader } from "../../components/ui/PageHeader";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorState } from "../../components/ui/ErrorState";
import { EmptyState } from "../../components/ui/EmptyState";
import { Badge } from "../../components/ui/Badge";

export function ScenarioList() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => api.scenarios.list({ size: 50 }),
  });

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorState />;

  const scenarios = data?.items ?? [];

  return (
    <div>
      <PageHeader
        title="Scenario Browser"
        subtitle={`${data?.meta?.total ?? 0} scenarios defined`}
      />

      {scenarios.length === 0 ? (
        <EmptyState message="No scenarios defined." />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {scenarios.map((s) => (
            <div
              key={s.id}
              className="card hover:border-accent transition-colors cursor-default"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-heading font-semibold text-text-primary">
                    {s.name}
                  </p>
                  <p className="text-caption font-mono text-text-secondary mt-0.5">
                    {s.code}
                  </p>
                </div>
                <div className="flex gap-1 flex-wrap justify-end">
                  {!s.is_active && <Badge variant="default">inactive</Badge>}
                  {s.is_regulatory && <Badge variant="accent">Regulatory</Badge>}
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

              {s.description && (
                <p className="text-body text-text-secondary mb-3 line-clamp-2">
                  {s.description}
                </p>
              )}

              <div className="flex items-center justify-between text-caption text-text-secondary">
                <span className="capitalize">
                  {s.scenario_type.replace(/_/g, " ")}
                </span>
                <span>
                  Created {format(new Date(s.created_at), "dd MMM yyyy")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
