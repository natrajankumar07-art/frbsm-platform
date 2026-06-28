import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
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

const fmt = (v: string | number, d = 0) =>
  Number(v).toLocaleString("en-IN", { maximumFractionDigits: d });

const pct = (v: string | number) => `${(Number(v) * 100).toFixed(2)}%`;

export function LCRDashboard() {
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

  const { data: lcr, isLoading } = useQuery({
    queryKey: ["lcr", snapshotId, selected?.id],
    queryFn: () =>
      snapshotId && selected
        ? api.analytics.lcr(snapshotId, selected.id)
        : Promise.resolve(null),
    enabled: !!snapshotId && !!selected,
  });

  const barData = lcr
    ? [
        { name: "HQLA", value: Number(lcr.hqla_total), fill: "#2B5BD7" },
        {
          name: "Net Outflows",
          value: Number(lcr.net_cash_outflows),
          fill: "#B0312C",
        },
        {
          name: "Total Outflows",
          value: Number(lcr.total_outflows),
          fill: "#8B93A1",
        },
        {
          name: "Total Inflows",
          value: Number(lcr.total_inflows),
          fill: "#1F7A4A",
        },
      ]
    : [];

  return (
    <div>
      <PageHeader
        title="Liquidity Coverage Ratio"
        subtitle="Basel III LCR — 30-day stress horizon · HQLA / Net Cash Outflows ≥ 100%"
        actions={
          <SnapshotSelector value={snapshotId} onChange={setSnapshotId} />
        }
      />

      {isLoading ? (
        <LoadingSpinner />
      ) : !lcr ? (
        <EmptyState message="No LCR result found for this snapshot and entity. Select a different snapshot or entity." />
      ) : (
        <>
          <div className="flex items-center gap-3 mb-6">
            <Badge
              variant={lcr.passes ? "positive" : "critical"}
              className="text-body px-3 py-1"
            >
              {lcr.passes ? "PASS" : "FAIL"}
            </Badge>
            <span className="text-heading font-semibold text-text-primary">
              LCR = {pct(lcr.lcr_ratio)}
            </span>
            <span className="text-body text-text-secondary">
              (minimum: {pct(lcr.minimum_ratio)})
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-4">
            <MetricCard
              label="LCR Ratio"
              value={pct(lcr.lcr_ratio)}
              sub={`Min: ${pct(lcr.minimum_ratio)}`}
              status={lcr.passes ? "positive" : "critical"}
            />
            <MetricCard
              label="HQLA Total"
              value={fmt(lcr.hqla_total)}
              sub={`${lcr.currency} (crore)`}
            />
            <MetricCard
              label="Net Cash Outflows"
              value={fmt(lcr.net_cash_outflows)}
              sub="30-day stress NCO"
            />
            <MetricCard
              label="Inflow Cap"
              value={lcr.inflow_cap_applied ? "Applied" : "Not Applied"}
              sub="75% of outflows cap"
              status={lcr.inflow_cap_applied ? "warning" : "positive"}
            />
          </div>

          <div className="card mb-6">
            <h2 className="text-heading font-semibold text-text-primary mb-4">
              LCR Components
            </h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E6E4DE" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 12, fill: "#5A6270" }}
                  />
                  <YAxis
                    tick={{ fontSize: 12, fill: "#5A6270" }}
                    tickFormatter={(v) => v.toLocaleString("en-IN")}
                  />
                  <Tooltip
                    formatter={(v: number) =>
                      v.toLocaleString("en-IN", { maximumFractionDigits: 0 })
                    }
                  />
                  {barData.map((entry) => (
                    <Bar
                      key={entry.name}
                      dataKey="value"
                      fill={entry.fill}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h2 className="text-heading font-semibold text-text-primary mb-4">
              Detail
            </h2>
            <dl className="grid grid-cols-2 gap-x-8 gap-y-3">
              {[
                ["Total Outflows", fmt(lcr.total_outflows)],
                ["Total Inflows", fmt(lcr.total_inflows)],
                ["Net Cash Outflows (NCO)", fmt(lcr.net_cash_outflows)],
                ["HQLA Total", fmt(lcr.hqla_total)],
                ["LCR Ratio", pct(lcr.lcr_ratio)],
                ["Minimum Ratio", pct(lcr.minimum_ratio)],
                ["Inflow Cap Applied", lcr.inflow_cap_applied ? "Yes" : "No"],
                ["Currency", lcr.currency],
              ].map(([k, v]) => (
                <div key={k} className="border-b border-border pb-2">
                  <dt className="text-caption text-text-secondary">{k}</dt>
                  <dd className="text-body font-mono font-medium text-text-primary">
                    {v}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </>
      )}
    </div>
  );
}
