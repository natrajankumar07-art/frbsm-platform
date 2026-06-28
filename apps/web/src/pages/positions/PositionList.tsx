import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { api } from "../../lib/api";
import { PageHeader } from "../../components/ui/PageHeader";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorState } from "../../components/ui/ErrorState";
import { Badge } from "../../components/ui/Badge";

const HQLA_VARIANT = {
  level_1: "positive",
  level_2a: "accent",
  level_2b: "warning",
  ineligible: "default",
} as const;

const PAGE_SIZE = 20;

export function PositionList() {
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["positions", page],
    queryFn: () => api.positions.list({ page, size: PAGE_SIZE }),
  });

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorState />;

  const positions = data?.items ?? [];
  const totalPages = data?.meta?.pages ?? 1;

  return (
    <div>
      <PageHeader
        title="Position Browser"
        subtitle={`${data?.meta?.total?.toLocaleString() ?? 0} total positions`}
      />

      <div className="card overflow-x-auto p-0">
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface">
            <tr>
              {[
                "Date",
                "Product",
                "Asset Class",
                "HQLA Level",
                "Booked Amount",
                "CCY",
                "IFRS9 Stage",
                "Status",
              ].map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-caption font-medium text-text-secondary uppercase tracking-wide whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-surface-raised">
            {positions.map((p) => (
              <tr key={p.id} className="hover:bg-surface transition-colors">
                <td className="px-4 py-3 text-caption text-text-secondary font-mono whitespace-nowrap">
                  {format(new Date(p.reporting_date), "dd MMM yy")}
                </td>
                <td className="px-4 py-3 text-body font-medium text-text-primary whitespace-nowrap">
                  {p.product_code}
                </td>
                <td className="px-4 py-3 text-caption text-text-secondary whitespace-nowrap">
                  {p.asset_class}
                </td>
                <td className="px-4 py-3">
                  <Badge
                    variant={
                      HQLA_VARIANT[p.hqla_level as keyof typeof HQLA_VARIANT] ??
                      "default"
                    }
                  >
                    {p.hqla_level}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-body text-right font-mono tabular-nums text-text-primary whitespace-nowrap">
                  {Number(p.booked_amount).toLocaleString("en-IN", {
                    maximumFractionDigits: 0,
                  })}
                </td>
                <td className="px-4 py-3 text-caption text-text-secondary">
                  {p.currency}
                </td>
                <td className="px-4 py-3">
                  <Badge
                    variant={
                      p.ifrs9_stage === "stage_3"
                        ? "critical"
                        : p.ifrs9_stage === "stage_2"
                        ? "warning"
                        : "default"
                    }
                  >
                    {p.ifrs9_stage}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <Badge
                    variant={p.status === "active" ? "positive" : "default"}
                  >
                    {p.status}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="flex items-center justify-between px-4 py-3 border-t border-border">
          <p className="text-caption text-text-secondary">
            Page {page} of {totalPages} · {data?.meta?.total?.toLocaleString()} positions
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1.5 rounded border border-border text-caption text-text-secondary hover:border-accent disabled:opacity-40 transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="px-3 py-1.5 rounded border border-border text-caption text-text-secondary hover:border-accent disabled:opacity-40 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
