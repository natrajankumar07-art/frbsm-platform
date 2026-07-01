import { useEffect, useState } from "react";
import { useQuery, useQueries } from "@tanstack/react-query";
import { format } from "date-fns";
import { api } from "../../lib/api";
import { useEntity } from "../../context/EntityContext";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { BankHealthIndicator, type BankHealth } from "../../components/dashboard/BankHealthIndicator";
import { ExecutiveSAMPanel } from "../../components/dashboard/ExecutiveSAMPanel";
import { RegulatoryStatusGrid } from "../../components/dashboard/RegulatoryStatusGrid";
import { RiskHeatmap } from "../../components/dashboard/RiskHeatmap";
import { InsightCard } from "../../components/dashboard/InsightCard";
import { TrendChart, type TrendDataPoint } from "../../components/dashboard/TrendChart";
import { ExecutiveDashTimeline, type ExecutiveTimelineEvent } from "../../components/dashboard/ExecutiveDashTimeline";
import { ExecutiveReports } from "../../components/dashboard/ExecutiveReports";
import { AskSAMButton } from "../../components/dashboard/AskSAMButton";
import { AlertCenter } from "../../components/autonomous/AlertCenter";
import { ActivityFeed } from "../../components/autonomous/ActivityFeed";
import { RecommendationsPanel } from "../../components/autonomous/RecommendationsPanel";
import type { LCRResult, NSFRResult, CapitalResult, Snapshot } from "../../types/api";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function fetchAlerts(): Promise<{ alert_id: string; title: string; severity: string; message: string; snapshot_date: string }[]> {
  const r = await fetch("/api/v1/copilot/agent/alerts");
  if (!r.ok) return [];
  const data = (await r.json()) as { alerts: { alert_id: string; title: string; severity: string; message: string; snapshot_date: string }[] };
  return data.alerts ?? [];
}

function computeBankHealth(
  lcr: LCRResult | null | undefined,
  nsfr: NSFRResult | null | undefined,
  capital: CapitalResult | null | undefined
): { health: BankHealth; passCount: number; totalChecks: number } {
  const checks = [
    lcr !== undefined && lcr !== null ? lcr.passes : null,
    nsfr !== undefined && nsfr !== null ? nsfr.passes : null,
    capital !== undefined && capital !== null ? capital.passes_all : null,
  ].filter((v) => v !== null) as boolean[];

  const totalChecks = checks.length;
  const passCount = checks.filter(Boolean).length;
  const failCount = totalChecks - passCount;

  let health: BankHealth = "healthy";
  if (totalChecks === 0) health = "warning";
  else if (failCount >= 2) health = "critical";
  else if (failCount === 1) health = "warning";

  return { health, passCount, totalChecks };
}

function buildTimeline(
  snapshots: Snapshot[],
  alerts: { alert_id: string; title: string; severity: string; message: string; snapshot_date: string }[]
): ExecutiveTimelineEvent[] {
  const events: ExecutiveTimelineEvent[] = [];

  snapshots.slice(0, 3).forEach((s) => {
    events.push({
      id: `snap-${s.id}`,
      type: "snapshot_processed",
      title: "Snapshot Processed",
      detail: `${format(new Date(s.reporting_date), "dd MMM yyyy")} · ${s.position_count.toLocaleString()} positions · ${s.status}`,
      timestamp: s.frozen_at ?? s.created_at,
    });
    events.push({
      id: `eng-${s.id}`,
      type: "engines_executed",
      title: "Engines Executed",
      detail: "LCR, NSFR, Capital and Balance Sheet engines computed for this snapshot.",
      timestamp: s.frozen_at ?? s.created_at,
    });
  });

  alerts.slice(0, 4).forEach((a) => {
    events.push({
      id: `alert-${a.alert_id}`,
      type: "alert_raised",
      title: `Alert: ${a.title}`,
      detail: a.message,
      timestamp: a.snapshot_date
        ? new Date(a.snapshot_date).toISOString()
        : new Date().toISOString(),
    });
  });

  events.sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return events.slice(0, 10);
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function ExecutiveDashboard() {
  const { selected: entity } = useEntity();
  const [snapshotId, setSnapshotId] = useState<string>("");

  const { data: snapshotsData, isLoading: loadingSnaps } = useQuery({
    queryKey: ["snapshots"],
    queryFn: () => api.snapshots.list({ size: 8 }),
  });

  const snapshots = snapshotsData?.items ?? [];

  useEffect(() => {
    if (snapshots.length && !snapshotId) {
      setSnapshotId(snapshots[0].id);
    }
  }, [snapshots, snapshotId]);

  const { data: lcrData } = useQuery({
    queryKey: ["lcr", snapshotId, entity?.id],
    queryFn: () => api.analytics.lcr(snapshotId, entity!.id),
    enabled: !!snapshotId && !!entity,
  });

  const { data: nsfrData } = useQuery({
    queryKey: ["nsfr", snapshotId, entity?.id],
    queryFn: () => api.analytics.nsfr(snapshotId, entity!.id),
    enabled: !!snapshotId && !!entity,
  });

  const { data: capitalData } = useQuery({
    queryKey: ["capital", snapshotId, entity?.id],
    queryFn: () => api.analytics.capital(snapshotId, entity!.id),
    enabled: !!snapshotId && !!entity,
  });

  const { data: alerts } = useQuery({
    queryKey: ["executive-alerts"],
    queryFn: fetchAlerts,
    staleTime: 60_000,
  });

  // Trend data: last 5 snapshots
  const trendSnaps = snapshots.slice(0, 5);

  const trendLCR = useQueries({
    queries: trendSnaps.map((s) => ({
      queryKey: ["lcr-trend", s.id, entity?.id],
      queryFn: () => api.analytics.lcr(s.id, entity!.id),
      enabled: !!entity,
    })),
  });

  const trendNSFR = useQueries({
    queries: trendSnaps.map((s) => ({
      queryKey: ["nsfr-trend", s.id, entity?.id],
      queryFn: () => api.analytics.nsfr(s.id, entity!.id),
      enabled: !!entity,
    })),
  });

  const trendCapital = useQueries({
    queries: trendSnaps.map((s) => ({
      queryKey: ["capital-trend", s.id, entity?.id],
      queryFn: () => api.analytics.capital(s.id, entity!.id),
      enabled: !!entity,
    })),
  });

  if (loadingSnaps) return <LoadingSpinner />;

  // Compute bank health
  const lcr = lcrData ?? undefined;
  const nsfr = nsfrData ?? undefined;
  const capital = capitalData ?? undefined;
  const { health, passCount, totalChecks } = computeBankHealth(lcr, nsfr, capital);
  const alertList = alerts ?? [];
  const latestSnap = snapshots[0];

  // Build trend data
  const trendData: TrendDataPoint[] = trendSnaps
    .map((s, i) => ({
      date: s.reporting_date,
      lcr: trendLCR[i].data ? Number(trendLCR[i].data!.lcr_ratio) : undefined,
      nsfr: trendNSFR[i].data ? Number(trendNSFR[i].data!.nsfr_ratio) : undefined,
      cet1: trendCapital[i].data ? Number(trendCapital[i].data!.cet1_ratio) : undefined,
      leverage: trendCapital[i].data ? Number(trendCapital[i].data!.leverage_ratio) : undefined,
    }))
    .reverse();

  const timeline = buildTimeline(snapshots, alertList);

  // Insight card data
  const lcrPct = lcr ? `${(Number(lcr.lcr_ratio) * 100).toFixed(1)}%` : "—";
  const nsfrPct = nsfr ? `${(Number(nsfr.nsfr_ratio) * 100).toFixed(1)}%` : "—";
  const cet1Pct = capital ? `${(Number(capital.cet1_ratio) * 100).toFixed(1)}%` : "—";

  if (!entity) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <p className="text-heading font-semibold text-text-primary dark:text-gray-100">
          Select an entity to view the Executive Dashboard
        </p>
        <p className="text-body text-text-secondary dark:text-gray-400">
          Use the entity selector in the top bar to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8" data-testid="executive-dashboard">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary dark:text-gray-100">
            Executive Intelligence Dashboard
          </h1>
          <p className="text-body text-text-secondary dark:text-gray-400 mt-0.5">
            {entity.name} · {entity.jurisdiction} · {entity.regulator}
            {latestSnap && (
              <span>
                {" "}· As of {format(new Date(latestSnap.reporting_date), "dd MMM yyyy")}
              </span>
            )}
          </p>
        </div>
        <AskSAMButton
          context={`Provide a comprehensive executive briefing for ${entity.name} covering all regulatory metrics and recommendations.`}
          label="Ask SAM"
          size="sm"
          className="flex-shrink-0"
        />
      </div>

      {/* Row 1: Bank Health + SAM Panel */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <BankHealthIndicator
          health={health}
          passCount={passCount}
          totalChecks={totalChecks}
        />
        <div className="lg:col-span-2">
          <ExecutiveSAMPanel
            entityName={entity.name}
            snapshotDate={
              latestSnap
                ? format(new Date(latestSnap.reporting_date), "dd MMM yyyy")
                : undefined
            }
            health={health}
            alertCount={alertList.length}
          />
        </div>
      </div>

      {/* Row 2: Regulatory Status Grid */}
      <RegulatoryStatusGrid lcr={lcr} nsfr={nsfr} capital={capital} />

      {/* Row 3: Insight Cards + Risk Heatmap */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="grid grid-cols-2 gap-4">
          <InsightCard
            domain="liquidity"
            title="Liquidity"
            value={lcrPct}
            trend={
              lcr
                ? Number(lcr.lcr_ratio) >= 1.2
                  ? "up"
                  : Number(lcr.lcr_ratio) >= 1.0
                  ? "flat"
                  : "down"
                : "flat"
            }
            trendLabel={lcr?.passes ? "Passing" : lcr ? "Below Min" : ""}
            drivers={
              lcr
                ? [
                    `HQLA: ${Number(lcr.hqla_total).toLocaleString()} ${lcr.currency}`,
                    `Net Outflows: ${Number(lcr.net_cash_outflows).toLocaleString()} ${lcr.currency}`,
                    lcr.inflow_cap_applied ? "Inflow cap applied" : "No inflow cap",
                  ]
                : ["Awaiting analytics data"]
            }
            recommendation={
              lcr?.passes
                ? "LCR is above the regulatory minimum. Monitor HQLA composition quality."
                : "LCR requires attention. Review HQLA eligibility and outflow assumptions."
            }
            onAskSAM={() => {
              sessionStorage.setItem("bsm-copilot-prefill", `Explain the LCR position for ${entity.name} in detail.`);
              window.location.href = "/copilot";
            }}
          />
          <InsightCard
            domain="capital"
            title="Capital"
            value={cet1Pct}
            trend={
              capital
                ? capital.passes_all
                  ? "up"
                  : "down"
                : "flat"
            }
            trendLabel={capital?.passes_all ? "All Pass" : capital ? "Review" : ""}
            drivers={
              capital
                ? [
                    `Total RWA: ${Number(capital.total_rwa).toLocaleString()} ${capital.currency}`,
                    `Tier 1: ${(Number(capital.tier1_ratio) * 100).toFixed(1)}%`,
                    `Leverage: ${(Number(capital.leverage_ratio) * 100).toFixed(1)}%`,
                  ]
                : ["Awaiting analytics data"]
            }
            recommendation={
              capital?.passes_all
                ? "All capital ratios meet Basel III requirements. Continue monitoring RWA growth."
                : "One or more capital ratios require attention. Consult the CRO."
            }
            onAskSAM={() => {
              sessionStorage.setItem("bsm-copilot-prefill", `Explain the capital adequacy position for ${entity.name}.`);
              window.location.href = "/copilot";
            }}
          />
          <InsightCard
            domain="funding"
            title="Funding Stability"
            value={nsfrPct}
            trend={
              nsfr
                ? Number(nsfr.nsfr_ratio) >= 1.1
                  ? "up"
                  : Number(nsfr.nsfr_ratio) >= 1.0
                  ? "flat"
                  : "down"
                : "flat"
            }
            trendLabel={nsfr?.passes ? "Passing" : nsfr ? "Below Min" : ""}
            drivers={
              nsfr
                ? [
                    `ASF: ${Number(nsfr.available_stable_funding).toLocaleString()} ${nsfr.currency}`,
                    `RSF: ${Number(nsfr.required_stable_funding).toLocaleString()} ${nsfr.currency}`,
                  ]
                : ["Awaiting analytics data"]
            }
            recommendation={
              nsfr?.passes
                ? "Structural funding is stable. NSFR exceeds minimum requirements."
                : "NSFR requires attention. Review long-term funding strategy."
            }
            onAskSAM={() => {
              sessionStorage.setItem("bsm-copilot-prefill", `Explain the NSFR funding stability for ${entity.name}.`);
              window.location.href = "/copilot";
            }}
          />
          <InsightCard
            domain="stress"
            title="Stress Position"
            value={alertList.length === 0 ? "Clear" : `${alertList.length} Alert${alertList.length !== 1 ? "s" : ""}`}
            trend={alertList.length === 0 ? "up" : alertList.length <= 2 ? "flat" : "down"}
            trendLabel={alertList.length === 0 ? "No Issues" : "Active"}
            drivers={
              alertList.length > 0
                ? alertList
                    .slice(0, 3)
                    .map((a) => `${a.severity.toUpperCase()}: ${a.title}`)
                : ["No active regulatory alerts", "All checks passing"]
            }
            recommendation={
              alertList.length === 0
                ? "No stress alerts active. Continue regular monitoring cycles."
                : "Active alerts require management attention. Review alert details in AI Copilot."
            }
            onAskSAM={() => {
              sessionStorage.setItem("bsm-copilot-prefill", `Explain all active alerts for ${entity.name} and provide remediation guidance.`);
              window.location.href = "/copilot";
            }}
          />
        </div>
        <RiskHeatmap lcr={lcr} nsfr={nsfr} capital={capital} />
      </div>

      {/* Row 4: Trend Analytics */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TrendChart
          data={trendData}
          title="Liquidity Trends (LCR & NSFR)"
          metrics={["lcr", "nsfr"]}
        />
        <TrendChart
          data={trendData}
          title="Capital Trends (CET1 & Leverage)"
          metrics={["cet1", "leverage"]}
        />
      </div>

      {/* Row 5: Timeline + Reports */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ExecutiveDashTimeline events={timeline} />
        <ExecutiveReports />
      </div>

      {/* Row 6: Autonomous Intelligence */}
      <div>
        <h2 className="text-body font-semibold text-text-secondary dark:text-gray-400 mb-3 uppercase tracking-wide text-xs">
          Autonomous Intelligence — SAM
        </h2>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <AlertCenter />
          <RecommendationsPanel />
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
