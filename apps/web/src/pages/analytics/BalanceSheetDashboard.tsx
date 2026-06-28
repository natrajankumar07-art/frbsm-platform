import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { api } from "../../lib/api";
import { useEntity } from "../../context/EntityContext";
import { PageHeader } from "../../components/ui/PageHeader";
import { MetricCard } from "../../components/ui/MetricCard";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { EmptyState } from "../../components/ui/EmptyState";
import { Badge } from "../../components/ui/Badge";
import { SnapshotSelector } from "./SnapshotSelector";

const COLORS = [
  "#2B5BD7",
  "#1F7A4A",
  "#B8730F",
  "#B0312C",
  "#5A6270",
  "#8B93A1",
  "#0E1116",
  "#E6E4DE",
];

const fmt = (v: string | number, d = 0) =>
  Number(v).toLocaleString("en-IN", { maximumFractionDigits: d });

export function BalanceSheetDashboard() {
  const { selected } = useEntity();
  const [snapshotId, setSnapshotId] = useState("");

  const { data: snapshotsData } = useQuery({
    queryKey: ["snapshots"],
    queryFn: () => api.snapshots.list({ size: 20 }),
  });

  useEffect(() => {
    if (snapshotsData?.items?.length && !snapshotId) {
      setSnapshotId(snapshotsData.items[0].id);
    }
  }, [snapshotsData, snapshotId]);

  const { data: bs, isLoading } = useQuery({
    queryKey: ["balance-sheet", snapshotId, selected?.id],
    queryFn: () =>
      snapshotId && selected
        ? api.analytics.balanceSheet(snapshotId, selected.id)
        : Promise.resolve(null),
    enabled: !!snapshotId && !!selected,
  });

  const { data: posSummary } = useQuery({
    queryKey: ["position-summary", selected?.id, snapshotId],
    queryFn: () =>
      selected
        ? api.analytics.positionSummary(selected.id, snapshotId || undefined)
        : Promise.resolve(null),
    enabled: !!selected,
  });

  const assetClassData = posSummary
    ? Object.entries(posSummary.by_asset_class)
        .map(([name, value]) => ({ name, value: Number(value) }))
        .filter((d) => d.value > 0)
        .sort((a, b) => b.value - a.value)
        .slice(0, 8)
    : [];

  return (
    <div>
      <PageHeader
        title="Balance Sheet"
        subtitle="Aggregated position data — IFRS / RBI Format A"
        actions={
          <SnapshotSelector value={snapshotId} onChange={setSnapshotId} />
        }
      />

      {isLoading ? (
        <LoadingSpinner />
      ) : !bs ? (
        <EmptyState message="No balance sheet result found for this snapshot and entity." />
      ) : (
        <>
          <div className="flex items-center gap-3 mb-6">
            <Badge
              variant={bs.balances ? "positive" : "critical"}
              className="text-body px-3 py-1"
            >
              {bs.balances ? "BALANCED" : "OUT OF BALANCE"}
            </Badge>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-4">
            <MetricCard
              label="Total Assets"
              value={fmt(bs.total_assets)}
              sub={bs.currency}
            />
            <MetricCard
              label="Total Liabilities"
              value={fmt(bs.total_liabilities)}
              sub={bs.currency}
            />
            <MetricCard
              label="Total Equity"
              value={fmt(bs.total_equity)}
              sub={bs.currency}
              status="positive"
            />
            <MetricCard
              label="Off-Balance Sheet"
              value={fmt(bs.off_balance_sheet)}
              sub={bs.currency}
            />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="card">
              <h2 className="text-heading font-semibold text-text-primary mb-4">
                Balance Check
              </h2>
              <dl className="space-y-3">
                {[
                  ["Total Assets", fmt(bs.total_assets)],
                  ["Total Liabilities", fmt(bs.total_liabilities)],
                  ["Equity", fmt(bs.total_equity)],
                  [
                    "Liabilities + Equity",
                    fmt(
                      Number(bs.total_liabilities) + Number(bs.total_equity)
                    ),
                  ],
                ].map(([k, v]) => (
                  <div
                    key={k}
                    className="flex justify-between border-b border-border pb-2"
                  >
                    <dt className="text-body text-text-secondary">{k}</dt>
                    <dd className="text-body font-mono font-medium text-text-primary">
                      {v}
                    </dd>
                  </div>
                ))}
                <div className="flex justify-between pt-1">
                  <dt className="text-body text-text-secondary">Balance</dt>
                  <dd>
                    <Badge variant={bs.balances ? "positive" : "critical"}>
                      {bs.balances ? "✓ Balanced" : "✗ Mismatch"}
                    </Badge>
                  </dd>
                </div>
              </dl>
            </div>

            {assetClassData.length > 0 && (
              <div className="card">
                <h2 className="text-heading font-semibold text-text-primary mb-4">
                  Asset Class Breakdown
                </h2>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={assetClassData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        label={({ name, percent }) =>
                          `${name} (${(percent * 100).toFixed(0)}%)`
                        }
                        labelLine={false}
                      >
                        {assetClassData.map((_, i) => (
                          <Cell
                            key={i}
                            fill={COLORS[i % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(v: number) =>
                          v.toLocaleString("en-IN", { maximumFractionDigits: 0 })
                        }
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
