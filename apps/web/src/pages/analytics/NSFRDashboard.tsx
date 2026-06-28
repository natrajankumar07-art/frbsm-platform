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
  Cell,
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

export function NSFRDashboard() {
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

  const { data: nsfr, isLoading } = useQuery({
    queryKey: ["nsfr", snapshotId, selected?.id],
    queryFn: () =>
      snapshotId && selected
        ? api.analytics.nsfr(snapshotId, selected.id)
        : Promise.resolve(null),
    enabled: !!snapshotId && !!selected,
  });

  const barData = nsfr
    ? [
        {
          name: "ASF",
          value: Number(nsfr.available_stable_funding),
          fill: "#1F7A4A",
        },
        {
          name: "RSF",
          value: Number(nsfr.required_stable_funding),
          fill: "#B0312C",
        },
      ]
    : [];

  const surplus = nsfr
    ? Number(nsfr.available_stable_funding) - Number(nsfr.required_stable_funding)
    : 0;

  return (
    <div>
      <PageHeader
        title="Net Stable Funding Ratio"
        subtitle="Basel III NSFR — structural funding requirement · ASF / RSF ≥ 100%"
        actions={
          <SnapshotSelector value={snapshotId} onChange={setSnapshotId} />
        }
      />

      {isLoading ? (
        <LoadingSpinner />
      ) : !nsfr ? (
        <EmptyState message="No NSFR result found for this snapshot and entity." />
      ) : (
        <>
          <div className="flex items-center gap-3 mb-6">
            <Badge
              variant={nsfr.passes ? "positive" : "critical"}
              className="text-body px-3 py-1"
            >
              {nsfr.passes ? "PASS" : "FAIL"}
            </Badge>
            <span className="text-heading font-semibold text-text-primary">
              NSFR = {pct(nsfr.nsfr_ratio)}
            </span>
            <span className="text-body text-text-secondary">
              (minimum: {pct(nsfr.minimum_ratio)})
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-4">
            <MetricCard
              label="NSFR Ratio"
              value={pct(nsfr.nsfr_ratio)}
              sub={`Min: ${pct(nsfr.minimum_ratio)}`}
              status={nsfr.passes ? "positive" : "critical"}
            />
            <MetricCard
              label="Available Stable Funding"
              value={fmt(nsfr.available_stable_funding)}
              sub={`${nsfr.currency} (crore)`}
            />
            <MetricCard
              label="Required Stable Funding"
              value={fmt(nsfr.required_stable_funding)}
              sub={`${nsfr.currency} (crore)`}
            />
            <MetricCard
              label="ASF Surplus"
              value={fmt(Math.abs(surplus))}
              sub={surplus >= 0 ? "surplus" : "shortfall"}
              status={surplus >= 0 ? "positive" : "critical"}
            />
          </div>

          <div className="card mb-6">
            <h2 className="text-heading font-semibold text-text-primary mb-4">
              ASF vs RSF
            </h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={barData}
                  margin={{ top: 8, right: 16, left: 8, bottom: 0 }}
                >
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
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {barData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Bar>
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
                [
                  "Available Stable Funding (ASF)",
                  fmt(nsfr.available_stable_funding),
                ],
                [
                  "Required Stable Funding (RSF)",
                  fmt(nsfr.required_stable_funding),
                ],
                ["NSFR Ratio", pct(nsfr.nsfr_ratio)],
                ["Minimum Ratio", pct(nsfr.minimum_ratio)],
                ["ASF Surplus", fmt(Math.abs(surplus))],
                ["Currency", nsfr.currency],
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
